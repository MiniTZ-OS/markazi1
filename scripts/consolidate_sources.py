#!/usr/bin/env python3
"""Preserve accessible Git refs and unite tracked working trees into markazi1/main."""
import base64,hashlib,json,os,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(os.environ["GITHUB_WORKSPACE"]).resolve()
TARGET=os.environ.get("GITHUB_REPOSITORY","MMLabsAI/markazi1")
RESERVED=b"__MINITZ_SOURCE_VERSIONS__"
TOKEN_VARS={"MahdiTT96":"SOURCE_TOKEN_MAHDITT96","MMLabsAI":"SOURCE_TOKEN_MMLABSAI","mataghdisi96-source":"SOURCE_TOKEN_MATAGHDISI96_SOURCE"}
for k,v in {"GIT_AUTHOR_NAME":"MiniTZ Consolidation Bot","GIT_AUTHOR_EMAIL":"41898282+github-actions[bot]@users.noreply.github.com","GIT_COMMITTER_NAME":"MiniTZ Consolidation Bot","GIT_COMMITTER_EMAIL":"41898282+github-actions[bot]@users.noreply.github.com"}.items(): os.environ.setdefault(k,v)
COUNT={"branches":0,"tags":0,"pull_refs":0,"trees":0,"tree_entries":0,"unique_paths_added":0,"conflict_versions_added":0,"ref_push_failures":0,"lfs_failures":0}
def git(args,token=None,raw=False,check=True,input_data=None):
    env=os.environ.copy(); env["GIT_TERMINAL_PROMPT"]="0"
    if token:
        enc=base64.b64encode(("x-access-token:"+token).encode()).decode()
        env["GIT_CONFIG_COUNT"]="1"; env["GIT_CONFIG_KEY_0"]="http.https://github.com/.extraheader"; env["GIT_CONFIG_VALUE_0"]="AUTHORIZATION: basic "+enc
    p=subprocess.run(["git",*args],cwd=ROOT,env=env,input=input_data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode: raise RuntimeError("git "+" ".join(args[:4])+" failed: "+p.stderr.decode("utf-8","replace")[-800:])
    return (p.stdout,p.returncode,p.stderr.decode("utf-8","replace")) if raw else p.stdout.decode("utf-8","surrogateescape").strip()
def api(url,tok):
    req=urllib.request.Request(url,headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"MiniTZ-markazi1"})
    with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)
MAN=json.loads((ROOT/"sources.json").read_text())
S={x["full_name"].lower():dict(x) for x in MAN["sources"]}
TOKENS={}; TOKEN_ERRORS={}
for account,var in TOKEN_VARS.items():
    tok=os.environ.get(var,"").strip()
    if not tok: continue
    try:
        login=api("https://api.github.com/user",tok).get("login","")
        if str(login).lower()!=account.lower(): TOKEN_ERRORS[var]=f"identity mismatch; expected {account}, got {login}"; continue
        TOKENS[var]=tok; page=1
        while True:
            items=api("https://api.github.com/user/repos?visibility=all&affiliation=owner,collaborator,organization_member&per_page=100&page="+str(page),tok)
            if not isinstance(items,list) or not items: break
            for x in items:
                full=x.get("full_name","")
                if not full or full.lower()==TARGET.lower(): continue
                owner,repo=full.split("/",1); old=S.get(full.lower())
                if old is None: S[full.lower()]={"owner":owner,"repo":repo,"full_name":full,"default_branch":x.get("default_branch") or "main","visibility":"private" if x.get("private") else "public","token_env":var if x.get("private") else None}
                elif x.get("private") and not old.get("token_env"): old["token_env"]=var; old["visibility"]="private"
            if len(items)<100: break
            page+=1
    except Exception as e: TOKEN_ERRORS[var]=type(e).__name__+": "+str(e)[:120]
def listrefs(prefix): return [r for r in git(["for-each-ref","--format=%(refname)",prefix]).splitlines() if r]
def tree_entries(rev):
    data,rc,err=git(["ls-tree","-r","-z","--full-tree",rev],raw=True)
    if rc: raise RuntimeError(err[-500:])
    out=[]
    for rec in data.split(b"\0"):
        if not rec: continue
        meta,path=rec.split(b"\t",1); mode,typ,oid=meta.decode().split()
        out.append((path,(mode,typ,oid)))
    return out
# All tree composition uses existing Git object IDs; it does not unpack large working trees.
PATHS={}; FILES=set(); DIRS=set()
def add(path,val,replace=False):
    if not path or path.startswith(b"/") or any(p in (b"",b".",b"..") for p in path.split(b"/")): return False
    parts=path.split(b"/")
    if path in DIRS or any(b"/".join(parts[:i]) in FILES for i in range(1,len(parts))): return False
    if path in PATHS and not replace: return PATHS[path]==val
    PATHS[path]=val; FILES.add(path)
    for i in range(1,len(parts)): DIRS.add(b"/".join(parts[:i]))
    return True
def possible(path,val):
    if path in PATHS: return PATHS[path]==val
    parts=path.split(b"/")
    return path not in DIRS and not any(b"/".join(parts[:i]) in FILES for i in range(1,len(parts)))
def merge_entry(path,val,owner,repo,label):
    if not (path==RESERVED or path.startswith(RESERVED+b"/")) and possible(path,val):
        if path not in PATHS: add(path,val); COUNT["unique_paths_added"]+=1
        return
    alt=RESERVED+b"/"+owner.encode()+b"/"+repo.encode()+b"/"+label.encode("utf-8","surrogateescape")+b"/"+path
    if possible(alt,val):
        if alt not in PATHS: add(alt,val); COUNT["conflict_versions_added"]+=1
        return
    mode,typ,oid=val; fallback=RESERVED+b"/by-blob/"+oid[:2].encode()+b"/"+(oid+"-"+mode).encode()
    if fallback not in PATHS and possible(fallback,val): add(fallback,val); COUNT["conflict_versions_added"]+=1
def make_tree(mapping):
    root={}
    for path,val in mapping.items():
        node=root; parts=path.split(b"/")
        for p in parts[:-1]: node=node.setdefault(p,{})
        node[parts[-1]]=val
    def emit(node):
        rows=[]
        for name,val in node.items():
            if isinstance(val,dict):
                oid=emit(val); rows.append((name+b"/",b"040000 tree "+oid.encode()+b"\t"+name))
            else:
                mode,typ,oid=val; rows.append((name+b"/" if typ=="tree" else name,(mode+" "+typ+" "+oid).encode()+b"\t"+name))
        rows.sort(key=lambda x:x[0])
        data,rc,err=git(["mktree","-z"],raw=True,input_data=b"".join(row+b"\0" for _,row in rows))
        if rc: raise RuntimeError("mktree failed: "+err[-500:])
        return data.decode().strip()
    return emit(root)
def push_refs(specs,tok):
    ok=0
    for i in range(0,len(specs),25):
        batch=specs[i:i+25]; _,rc,_=git(["push","--porcelain","origin",*batch],token=tok,raw=True,check=False)
        if not rc: ok+=len(batch); continue
        for spec in batch:
            _,one,detail=git(["push","--porcelain","origin",spec],token=tok,raw=True,check=False)
            if one: COUNT["ref_push_failures"]+=1
            else: ok+=1
    return ok
base=git(["rev-parse","refs/heads/main"])
for p,v in tree_entries(git(["rev-parse",base+"^{tree}"])): add(p,v)
README="""# MiniTZ Central Repository

This repository consolidates tracked working-tree content and recoverable Git history from the connected GitHub accounts.

- main contains unique paths from source branch, tag and pull-request trees at their original relative paths.
- Conflicting versions are preserved under __MINITZ_SOURCE_VERSIONS__/OWNER/REPOSITORY/REF/PATH.
- Original branch SHAs are retained under source-branches/OWNER/REPOSITORY/BRANCH; snapshots retain earlier branch tips.
- Source tags use source-tags/OWNER/REPOSITORY/TAG. Pull-request refs use source-pulls/OWNER/REPOSITORY/NUMBER/TYPE.
- Original source repositories are read-only inputs. Only MMLabsAI/markazi1 is written.

For private sources, add the secrets SOURCE_TOKEN_MAHDITT96, SOURCE_TOKEN_MMLABSAI and SOURCE_TOKEN_MATAGHDISI96_SOURCE with read access to the corresponding accounts' source repos, including Git LFS. See IMPORT_REPORT.md for evidence and omissions.
"""
ro=git(["hash-object","-w","--stdin"],raw=True,input_data=README.encode())[0].decode().strip()
old=PATHS.get(b"README.md")
if old and old[2]!=ro: merge_entry(b"README.md",old,"MMLabsAI","markazi1","bootstrap")
add(b"README.md",("100644","blob",ro),True)
RESULTS=[]; SKIPPED=[]
for src in sorted(S.values(),key=lambda x:x["full_name"].lower()):
    full=src["full_name"]
    if full.lower()==TARGET.lower(): continue
    owner,repo=src["owner"],src["repo"]; tenv=src.get("token_env"); tok=TOKENS.get(tenv) if tenv else None
    if src.get("visibility")=="private" and not tok:
        SKIPPED.append(full); RESULTS.append({"repo":full,"status":"SKIPPED_MISSING_TOKEN","secret":tenv}); continue
    slug=hashlib.sha256(full.lower().encode()).hexdigest()[:12]; rem="src_"+slug; tr="tag_"+slug; pr="pr_"+slug
    git(["remote","add",rem,src.get("clone_url") or "https://github.com/"+full+".git"],check=False)
    bp="refs/remotes/"+rem+"/"; tp="refs/remotes/"+tr+"/"; pp="refs/remotes/"+pr+"/"
    _,rc,err=git(["fetch","--no-tags","--no-recurse-submodules",rem,"+refs/heads/*:"+bp+"*","+refs/tags/*:"+tp+"*"],token=tok,raw=True,check=False)
    if rc: RESULTS.append({"repo":full,"status":"FETCH_FAILED","detail":err[-250:]}); continue
    pull_notes=[]
    for spec in ["+refs/pull/*/head:"+pp+"*/head","+refs/pull/*/merge:"+pp+"*/merge"]:
        _,prc,pe=git(["fetch","--no-tags",rem,spec],token=tok,raw=True,check=False)
        if prc and pe.strip(): pull_notes.append(pe.strip()[-120:])
    br=listrefs(bp); tags=listrefs(tp); pulls=listrefs(pp)
    COUNT["branches"]+=len(br); COUNT["tags"]+=len(tags); COUNT["pull_refs"]+=len(pulls)
    specs=[]; trees=[]; default=src.get("default_branch") or "main"
    for r in br:
        name=r[len(bp):]; oid=git(["rev-parse",r])
        specs += ["+"+oid+f":refs/heads/source-branches/{owner}/{repo}/{name}",oid+f":refs/heads/source-snapshots/{owner}/{repo}/{name}/{oid}"]
        trees.append((r,"branches/"+name,0 if name==default else 1))
    for r in tags:
        name=r[len(tp):]; oid=git(["rev-parse",r])
        specs += ["+"+oid+f":refs/tags/source-tags/{owner}/{repo}/{name}",oid+f":refs/tags/source-tag-snapshots/{owner}/{repo}/{name}/{oid}"]
        trees.append((r,"tags/"+name,3))
    for r in pulls:
        name=r[len(pp):]; oid=git(["rev-parse",r])
        specs += ["+"+oid+f":refs/heads/source-pulls/{owner}/{repo}/{name}",oid+f":refs/heads/source-pull-snapshots/{owner}/{repo}/{name}/{oid}"]
        trees.append((r,"pulls/"+name,2))
    pushed=push_refs(specs,os.environ.get("GITHUB_TOKEN","")) if specs else 0
    lfs="not_checked"
    try:
        probe=subprocess.run(["git","lfs","version"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if probe.returncode: lfs="git-lfs unavailable"
        elif shutil.disk_usage(ROOT).free<3*1024**3: lfs="skipped-low-disk"
        else:
            _,lr,le=git(["lfs","fetch","--all",rem],token=tok,raw=True,check=False)
            if lr: lfs="fetch-failed"; COUNT["lfs_failures"]+=1
            else:
                ok=True
                for i in range(0,len(trees),25):
                    _,prc,_=git(["lfs","push","--all","origin",*[x[0] for x in trees[i:i+25]]],token=os.environ.get("GITHUB_TOKEN",""),raw=True,check=False)
                    if prc: ok=False; lfs="push-failed"; COUNT["lfs_failures"]+=1; break
                if ok: lfs="uploaded"
            shutil.rmtree(ROOT/".git"/"lfs"/"objects",ignore_errors=True); (ROOT/".git"/"lfs"/"objects").mkdir(parents=True,exist_ok=True)
    except Exception: lfs="error"; COUNT["lfs_failures"]+=1
    trees.sort(key=lambda x:(x[2],x[1])); tn=0; fn=0; errs=[]
    for r,label,_ in trees:
        commit=git(["rev-parse",r+"^{commit}"],check=False)
        if not commit: continue
        try:
            for p,v in tree_entries(commit): merge_entry(p,v,owner,repo,label); fn+=1
            tn+=1
        except Exception as e: errs.append(label+":"+type(e).__name__)
    COUNT["trees"]+=tn; COUNT["tree_entries"]+=fn
    state="IMPORTED" if pushed==len(specs) and not errs and lfs=="uploaded" else "PARTIAL"
    RESULTS.append({"repo":full,"status":state,"branches":len(br),"tags":len(tags),"pull_refs":len(pulls),"refs_pushed":pushed,"expected_refs":len(specs),"trees":tn,"entries":fn,"lfs":lfs,"tree_errors":errs[:8],"pull_notes":pull_notes})
missing=sorted(v for v in TOKEN_VARS.values() if v not in TOKENS)
full_complete=not SKIPPED and not missing and not TOKEN_ERRORS and not COUNT["ref_push_failures"] and not COUNT["lfs_failures"] and all(x.get("status")=="IMPORTED" for x in RESULTS)
lines=["# Import Report","",f"Run result: {'COMPLETE' if full_complete else 'PARTIAL'}","",f"Target: {TARGET}"]
lines += [f"{k.replace('_',' ')}: {v}" for k,v in COUNT.items()]
lines += ["","## Required secrets"]+["- "+x for x in missing]
lines += ["","## Private repositories skipped"]+["- "+x for x in SKIPPED]
lines += ["","## Token errors"]+[f"- {k}: {v}" for k,v in TOKEN_ERRORS.items()]
lines += ["","## Repository results","","| Repository | Status | Branches | Tags | PR refs | Trees | LFS |","|---|---|---:|---:|---:|---:|---|"]
for x in RESULTS: lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(x.get("repo"),x.get("status"),x.get("branches",0),x.get("tags",0),x.get("pull_refs",0),x.get("trees",0),x.get("lfs","—")))
lines += ["","## Known omissions","- GitHub release assets are not Git refs and are not copied by this workflow.","- A missing source token means that private repository and any additional account-only repositories cannot be imported.","- LFS skip/failure means its payload still needs transfer."]
report_oid=git(["hash-object","-w","--stdin"],raw=True,input_data=("\n".join(lines)+"\n").encode())[0].decode().strip()
add(b"IMPORT_REPORT.md",("100644","blob",report_oid),True)
newtree=make_tree(PATHS)
newcommit=git(["commit-tree",newtree,"-p",base,"-m","Consolidate accessible repository refs and working trees"])
git(["update-ref","refs/heads/main",newcommit,base])
_,rc,err=git(["push","origin","refs/heads/main:refs/heads/main"],token=os.environ.get("GITHUB_TOKEN",""),raw=True,check=False)
if rc: print("MAIN_PUSH_FAILED: "+err[-1400:],file=sys.stderr); sys.exit(2)
print(json.dumps({"result":"COMPLETE" if full_complete else "PARTIAL","counts":COUNT,"skipped_private":SKIPPED,"missing_secrets":missing,"token_errors":TOKEN_ERRORS,"repositories":RESULTS},indent=2))
