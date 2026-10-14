#!/usr/bin/env python3
"""Import source refs verbatim and unite their tracked trees in main."""
import base64, hashlib, json, os, shutil, subprocess, sys, urllib.request
from pathlib import Path

ROOT=Path(os.environ["GITHUB_WORKSPACE"]).resolve()
TARGET=os.environ.get("GITHUB_REPOSITORY","MMLabsAI/markazi1")
RESERVED=b"__MINITZ_SOURCE_VERSIONS__"
TOKEN_NAMES={"MahdiTT96":"SOURCE_TOKEN_MAHDITT96","MMLabsAI":"SOURCE_TOKEN_MMLABSAI","mataghdisi96-source":"SOURCE_TOKEN_MATAGHDISI96_SOURCE"}
for k,v in {"GIT_AUTHOR_NAME":"MiniTZ Consolidation Bot","GIT_AUTHOR_EMAIL":"41898282+github-actions[bot]@users.noreply.github.com","GIT_COMMITTER_NAME":"MiniTZ Consolidation Bot","GIT_COMMITTER_EMAIL":"41898282+github-actions[bot]@users.noreply.github.com"}.items():
    os.environ.setdefault(k,v)
COUNTS={"repos_ok":0,"branch_refs":0,"tag_refs":0,"pull_refs":0,"tree_refs":0,"tree_entries":0,"root_files_added":0,"source_versions_added":0,"push_failures":0,"lfs_failures":0}
ERRORS=[]

def git(args,token=None,raw=False,check=True,input_data=None):
    env=os.environ.copy()
    env["GIT_TERMINAL_PROMPT"]="0"
    if token:
        enc=base64.b64encode(("x-access-token:"+token).encode()).decode()
        env["GIT_CONFIG_COUNT"]="1"; env["GIT_CONFIG_KEY_0"]="http.https://github.com/.extraheader"
        env["GIT_CONFIG_VALUE_0"]="AUTHORIZATION: basic "+enc
    p=subprocess.run(["git",*args],cwd=ROOT,env=env,input=input_data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError("git "+" ".join(args[:4])+" failed: "+p.stderr.decode("utf-8","replace")[-1200:])
    if raw:
        return p.stdout,p.returncode,p.stderr.decode("utf-8","replace")
    return p.stdout.decode("utf-8","surrogateescape").strip()

def api(url,token):
    req=urllib.request.Request(url,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"MiniTZ-markazi1-consolidator"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)

manifest=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
SOURCES={x["full_name"].lower():dict(x) for x in manifest["sources"]}
TOKENS={}; TOKEN_ERRORS={}
# Verify configured token identity, then enumerate all repositories visible to each source account.
for account,var in TOKEN_NAMES.items():
    token=os.environ.get(var,"").strip()
    if not token: continue
    try:
        who=api("https://api.github.com/user",token).get("login","")
        if str(who).lower()!=account.lower():
            TOKEN_ERRORS[var]=f"identity mismatch: expected {account}, received {who or 'unknown'}"; continue
        TOKENS[var]=token
        page=1
        while True:
            url="https://api.github.com/user/repos?visibility=all&affiliation=owner,collaborator,organization_member&per_page=100&page="+str(page)
            try: items=api(url,token)
            except Exception as e:
                TOKEN_ERRORS.setdefault(var,"repo discovery unavailable: "+type(e).__name__); break
            if not isinstance(items,list) or not items: break
            for item in items:
                full=item.get("full_name","")
                if not full or full.lower()==TARGET.lower(): continue
                owner,repo=full.split("/",1)
                old=SOURCES.get(full.lower())
                if old is None:
                    SOURCES[full.lower()]={"owner":owner,"repo":repo,"full_name":full,"default_branch":item.get("default_branch") or "main","visibility":"private" if item.get("private") else "public","token_env":var if item.get("private") else None}
                elif item.get("private") and not old.get("token_env"):
                    old["token_env"]=var; old["visibility"]="private"
            if len(items)<100: break
            page+=1
    except Exception as e:
        TOKEN_ERRORS[var]="token validation/discovery failed: "+type(e).__name__

def refs(prefix):
    return [x for x in git(["for-each-ref","--format=%(refname)",prefix]).splitlines() if x]

def rev(ref): return git(["rev-parse",ref])

def tree_entries(revision):
    raw,rc,err=git(["ls-tree","-r","-z","--full-tree",revision],raw=True)
    if rc: raise RuntimeError(err[-800:])
    out=[]
    for row in raw.split(b"\0"):
        if not row: continue
        meta,path=row.split(b"\t",1)
        mode,typ,oid=meta.decode("ascii").split(" ")
        out.append((path,(mode,typ,oid)))
    return out

# Keep existing target files and build trees from object IDs; no giant source worktrees are unpacked.
entries={}; file_paths=set(); dir_paths=set()
def add_entry(path,entry,replace=False):
    if not path or path.startswith(b"/") or any(p in (b"",b".",b"..") for p in path.split(b"/")): return False
    parts=path.split(b"/")
    if any(b"/".join(parts[:i]) in file_paths for i in range(1,len(parts))): return False
    if path in dir_paths: return False
    if path in entries and not replace: return entries[path]==entry
    entries[path]=entry; file_paths.add(path)
    for i in range(1,len(parts)): dir_paths.add(b"/".join(parts[:i]))
    return True

def can_place(path,entry):
    if path in entries: return entries[path]==entry
    parts=path.split(b"/")
    return not any(b"/".join(parts[:i]) in file_paths for i in range(1,len(parts))) and path not in dir_paths

def add_source(path,entry,owner,repo,label):
    if not (path==RESERVED or path.startswith(RESERVED+b"/")) and can_place(path,entry):
        if path not in entries:
            add_entry(path,entry); COUNTS["root_files_added"]+=1
        return
    alt=RESERVED+b"/"+owner.encode()+b"/"+repo.encode()+b"/"+label.encode("utf-8","surrogateescape")+b"/"+path
    if can_place(alt,entry):
        if alt not in entries: add_entry(alt,entry); COUNTS["source_versions_added"]+=1
        return
    mode,typ,oid=entry
    fallback=RESERVED+b"/by-blob/"+oid[:2].encode()+b"/"+(oid+"-"+mode).encode()
    if can_place(fallback,entry) and fallback not in entries:
        add_entry(fallback,entry); COUNTS["source_versions_added"]+=1
    elif fallback not in entries:
        raise RuntimeError("cannot place conflicting blob "+oid)

def build_tree(path_map):
    root={}
    for path,entry in path_map.items():
        node=root; pieces=path.split(b"/")
        for p in pieces[:-1]: node=node.setdefault(p,{})
        node[pieces[-1]]=entry
    def emit(node):
        rows=[]
        for name,value in node.items():
            if isinstance(value,dict):
                oid=emit(value); rows.append((name+b"/",b"040000 tree "+oid.encode()+b"\t"+name))
            else:
                mode,typ,oid=value
                rows.append((name+b"/" if typ=="tree" else name,(mode+" "+typ+" "+oid).encode()+b"\t"+name))
        rows.sort(key=lambda x:x[0])
        payload=b"".join(row+b"\0" for _,row in rows)
        out,rc,err=git(["mktree","-z"],raw=True,input_data=payload)
        if rc: raise RuntimeError("mktree failed: "+err[-800:])
        return out.decode().strip()
    return emit(root)

def push_many(specs,token):
    count=0
    for i in range(0,len(specs),30):
        batch=specs[i:i+30]
        _,rc,err=git(["push","--porcelain","origin",*batch],token=token,raw=True,check=False)
        if rc==0: count+=len(batch); continue
        for spec in batch:
            _,one_rc,one_err=git(["push","--porcelain","origin",spec],token=token,raw=True,check=False)
            if one_rc==0: count+=1
            else:
                COUNTS["push_failures"]+=1
                ERRORS.append({"refspec":spec,"detail":one_err[-300:]})
    return count

base=git(["rev-parse","refs/heads/main"])
for path,entry in tree_entries(git(["rev-parse",base+"^{tree}"])):
    add_entry(path,entry)

README="""# MiniTZ Central Repository

This repository consolidates recoverable Git history and working-tree content from repositories visible to the connected GitHub accounts.

## Structure and preservation

- main contains the union of tracked working-tree paths. Unique paths stay at their original relative paths.
- Conflicting versions are retained under __MINITZ_SOURCE_VERSIONS__/OWNER/REPOSITORY/REF/PATH.
- Source branch SHAs are preserved under source-branches/OWNER/REPOSITORY/BRANCH.
- Tags are preserved under source-tags/OWNER/REPOSITORY/TAG.
- Pull-request head and merge refs are preserved under source-pulls/OWNER/REPOSITORY/NUMBER/TYPE.
- Content-addressed snapshot refs retain earlier branch tips when a source branch is force-pushed.
- Source repositories are read-only inputs. This workflow writes only to MMLabsAI/markazi1.

## Private source access

Add read-capable personal access tokens as these repository Actions secrets for the corresponding accounts: SOURCE_TOKEN_MAHDITT96, SOURCE_TOKEN_MMLABSAI, SOURCE_TOKEN_MATAGHDISI96_SOURCE. Tokens must be able to read the private repositories (including Git LFS). The workflow token writes only to this central repository.

See IMPORT_REPORT.md for the latest evidence and outstanding omissions.
"""
readme_oid=git(["hash-object","-w","--stdin"],raw=True,input_data=README.encode())[0].decode().strip()
old=entries.get(b"README.md")
if old and old[2]!=readme_oid: add_source(b"README.md",old,"MMLabsAI","markazi1","bootstrap")
add_entry(b"README.md",("100644","blob",readme_oid),replace=True)

statuses=[]; missing_private=[]
for src in sorted(SOURCES.values(),key=lambda s:s["full_name"].lower()):
    full=src["full_name"]
    if full.lower()==TARGET.lower(): continue
    owner,repo=src["owner"],src["repo"]
    token_env=src.get("token_env"); token=TOKENS.get(token_env) if token_env else None
    if src.get("visibility")=="private" and not token:
        missing_private.append(full)
        statuses.append({"repository":full,"status":"SKIPPED_MISSING_SOURCE_TOKEN","secret":token_env}); continue
    slug=hashlib.sha256(full.lower().encode()).hexdigest()[:12]
    remote="src_"+slug; tag_remote="tag_"+slug; pull_remote="pr_"+slug
    git(["remote","add",remote,src.get("clone_url") or "https://github.com/"+full+".git"],check=False)
    bp="refs/remotes/"+remote+"/"; tp="refs/remotes/"+tag_remote+"/"; pp="refs/remotes/"+pull_remote+"/"
    _,frc,ferr=git(["fetch","--no-tags","--no-recurse-submodules",remote,
                     "+refs/heads/*:"+bp+"*","+refs/tags/*:"+tp+"*"],token=token,raw=True,check=False)
    if frc:
        statuses.append({"repository":full,"status":"FETCH_FAILED","detail":ferr[-800:]}); continue
    pull_notes=[]
    for spec in ["+refs/pull/*/head:"+pp+"*/head","+refs/pull/*/merge:"+pp+"*/merge"]:
        _,rc,err=git(["fetch","--no-tags",remote,spec],token=token,raw=True,check=False)
        if rc and err.strip(): pull_notes.append(err.strip()[-200:])
    branch_refs=refs(bp); tag_refs=refs(tp); pull_refs=refs(pp)
    COUNTS["branch_refs"]+=len(branch_refs); COUNTS["tag_refs"]+=len(tag_refs); COUNTS["pull_refs"]+=len(pull_refs)
    push_list=[]; source_trees=[]; default=src.get("default_branch") or "main"
    for ref in branch_refs:
        name=ref[len(bp):]; oid=rev(ref)
        push_list.extend(["+"+oid+f":refs/heads/source-branches/{owner}/{repo}/{name}",
                          oid+f":refs/heads/source-snapshots/{owner}/{repo}/{name}/{oid}"])
        source_trees.append((ref,"branches/"+name,0 if name==default else 1))
    for ref in tag_refs:
        name=ref[len(tp):]; oid=rev(ref)
        push_list.extend(["+"+oid+f":refs/tags/source-tags/{owner}/{repo}/{name}",
                          oid+f":refs/tags/source-tag-snapshots/{owner}/{repo}/{name}/{oid}"])
        source_trees.append((ref,"tags/"+name,3))
    for ref in pull_refs:
        name=ref[len(pp):]; oid=rev(ref)
        push_list.extend(["+"+oid+f":refs/heads/source-pulls/{owner}/{repo}/{name}",
                          oid+f":refs/heads/source-pull-snapshots/{owner}/{repo}/{name}/{oid}"])
        source_trees.append((ref,"pulls/"+name,2))
    pushed=push_many(push_list,os.environ.get("GITHUB_TOKEN","")) if push_list else 0

    # Transfer LFS payloads where the runner has sufficient free disk; ref transfer is independent.
    lfs="not_checked"
    try:
        probe=subprocess.run(["git","lfs","version"],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if probe.returncode: lfs="git-lfs unavailable"
        elif shutil.disk_usage(ROOT).free < 3*1024**3: lfs="skipped: less than 3 GiB free"
        else:
            _,lrc,lerr=git(["lfs","fetch","--all",remote],token=token,raw=True,check=False)
            if lrc:
                lfs="fetch failed: "+lerr[-250:]; COUNTS["lfs_failures"]+=1
            else:
                refnames=[r for r,_,_ in source_trees]
                uploaded=True
                for i in range(0,len(refnames),25):
                    _,prc,perr=git(["lfs","push","--all","origin",*refnames[i:i+25]],token=os.environ.get("GITHUB_TOKEN",""),raw=True,check=False)
                    if prc:
                        uploaded=False; lfs="push failed: "+perr[-250:]; COUNTS["lfs_failures"]+=1; break
                if uploaded: lfs="uploaded for imported refs"
            shutil.rmtree(ROOT/".git"/"lfs"/"objects",ignore_errors=True)
            (ROOT/".git"/"lfs"/"objects").mkdir(parents=True,exist_ok=True)
    except Exception as exc:
        lfs="error: "+type(exc).__name__; COUNTS["lfs_failures"]+=1

    tree_n=0; file_n=0; tree_errors=[]
    source_trees.sort(key=lambda x:(x[2],x[1]))
    for ref,label,_ in source_trees:
        commit=git(["rev-parse",ref+"^{commit}"],check=False)
        if not commit: continue
        try:
            for path,entry in tree_entries(commit):
                add_source(path,entry,owner,repo,label); file_n+=1
            tree_n+=1
        except Exception as exc:
            tree_errors.append(label+": "+type(exc).__name__+": "+str(exc)[:250])
    COUNTS["tree_refs"]+=tree_n; COUNTS["tree_entries"]+=file_n; COUNTS["repos_ok"]+=1
    bad_lfs=lfs.startswith(("fetch failed","push failed","skipped","error","git-lfs"))
    status="IMPORTED" if pushed==len(push_list) and not tree_errors and not bad_lfs else "PARTIAL"
    statuses.append({"repository":full,"status":status,"branches":len(branch_refs),"tags":len(tag_refs),
        "pull_refs":len(pull_refs),"refs_pushed":pushed,"expected_refs":len(push_list),
        "trees_merged":tree_n,"tree_entries":file_n,"lfs":lfs,"pull_notes":pull_notes,"tree_errors":tree_errors[:12]})

missing_secrets=sorted(v for v in TOKEN_NAMES.values() if v not in TOKENS)
complete=(not missing_private and not missing_secrets and not TOKEN_ERRORS and not COUNTS["push_failures"]
          and not COUNTS["lfs_failures"] and all(s.get("status")=="IMPORTED" for s in statuses))
result={"target":TARGET,"result":"COMPLETE" if complete else "PARTIAL",
        "missing_secrets":missing_secrets,"private_repositories_skipped":sorted(missing_private),
        "token_errors":TOKEN_ERRORS,"counts":COUNTS,"repositories":statuses,
        "notes":["GitHub release assets are not Git refs and are not copied by this workflow.",
                 "A third-account token is required for runtime discovery because its connected inventory returned zero repositories.",
                 "A skipped or failed LFS transfer means the associated LFS payloads are still missing from the target."]}
lines=["# Import Report","",f"**Run result: {result['result']}**","",f"- Target: {TARGET}"]
for key,value in COUNTS.items(): lines.append(f"- {key.replace('_',' ')}: {value}")
lines += ["","## Required secrets"]+[f"- {x}" for x in missing_secrets]
lines += ["","## Private repositories skipped"]+[f"- {x} (needs {SOURCES[x.lower()].get('token_env')})" for x in sorted(missing_private)]
lines += ["","## Token discovery"]+[f"- {k}: {v}" for k,v in TOKEN_ERRORS.items()]
lines += ["","## Per-repository result","","| Repository | Status | Branches | Tags | PR refs | Trees merged | LFS |","|---|---|---:|---:|---:|---:|---|"]
for x in statuses:
    lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(x.get("repository","?"),x.get("status","?"),
        x.get("branches",0),x.get("tags",0),x.get("pull_refs",0),x.get("trees_merged",0),str(x.get("lfs","—")).replace("|","/")))
lines += ["","## Notes",""]+[f"- {x}" for x in result["notes"]]
report_oid=git(["hash-object","-w","--stdin"],raw=True,input_data=("\n".join(lines)+"\n").encode())[0].decode().strip()
add_entry(b"IMPORT_REPORT.md",("100644","blob",report_oid),replace=True)
tree_oid=build_tree(entries)
commit=git(["commit-tree",tree_oid,"-p",base,"-m","Consolidate accessible repositories, branches, tags and working trees"])
git(["update-ref","refs/heads/main",commit,base])
_,push_rc,push_err=git(["push","origin","refs/heads/main:refs/heads/main"],token=os.environ.get("GITHUB_TOKEN",""),raw=True,check=False)
if push_rc:
    print("MAIN_PUSH_FAILED: "+push_err[-2000:],file=sys.stderr); sys.exit(2)
print(json.dumps(result,indent=2))
