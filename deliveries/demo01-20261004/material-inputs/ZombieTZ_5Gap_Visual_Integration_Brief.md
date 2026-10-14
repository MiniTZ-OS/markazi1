# ZombieTZ — five-gap visual integration brief

Prepared 4 October 2026. Target project: ZombieTZ / Harbor Nine on RTX `minitz.m`.

This is an implementation specification, not a deployed repair or rendered acceptance. The verified baseline below is the 30 September capture and source diagnosis. The imported upgrade pack was delivered later that morning; its materials were not assigned to the level and no game package was rebuilt for that delivery. Current source, runtime and asset compatibility must be read before applying this brief.

## The five gaps and the concrete correction

| Gap | Verified baseline | Correction to implement | Evidence required before calling it repaired |
|---|---|---|---|
| 1. Player presentation | `BiellaDemoPawn.cpp` loads `SKM_Manny_Simple`, applies presentation material instances and attaches harness/backpack at `spine_03`; two gear components logged. | Calibrate existing gear/material response first. A finished survivor requires a separately verified human skeletal asset, skin/clothing textures, skeleton/animation compatibility and fitting. Denim texture is only a gear candidate. | Neutral-light player close-up, front/back and moving third-person capture; no gear clipping in idle/run/crouch; report actual mesh/material paths. Do not call a recolored mannequin a completed character. |
| 2. Sparse modular environment | `HarborNineEnvironment.cpp` builds ten instanced mesh categories and uses four material families; canopy reuses wall/pipe-rack/floor meshes. | Assign the existing eight surface candidates by physical purpose, then dress one representative route section with delivered props and authored edge/detail layers. Preserve route geometry and collision. | Same-camera before/after, material-slot inventory, scale/tiling close-ups and uninterrupted traversal through that section. Geometry density and readable silhouette must improve, not just color variation. |
| 3. Lighting/exposure imbalance | 48 route work lights: 24,000 intensity, 7,000 cm radius, shadows disabled. Eight warehouse fills: 18,000 lumens, 3,800 cm radius, shadows disabled. Exposure min/max 3/6 with extended luminance range enabled. Dated diagnosis observes bright sky and dark structures. | Isolate exposure, sky and practical lights in controlled captures. Establish a fixed EV100 test exposure, then tune the sky and a small set of practical lights with fixtures, local falloff and selective shadows. Final adaptive exposure follows only after the fixed test is coherent. | Record effective post-process overrides and actual light units; matched fixed-exposure captures with sky only, practicals only and combined. Retain texture detail in sky-facing and shadowed surfaces. |
| 4. Rendering target mismatch | Captured Linux log selects `VULKAN_SM5` and reports Vulkan ray tracing disabled because SM6 is required. Windows target alone configures DX12/SM6. | Inspect the installed engine's Linux target settings, host Vulkan/device capabilities and actual cook profile; configure and recook the intended supported shader platform in the existing project. Keep hardware RT acceptance separate from software Lumen. | Fresh packaged runtime log names the intended shader platform, records enabled/disabled RT with its reason, and is tied to executable/source/package hashes. A settings change or RTX host name alone is insufficient. |
| 5. HUD readability | `Demo01HUD.cpp` draws near-white primary text directly; no core-line backdrop or outline/shadow in inspected source. Low contrast over bright background is visible in dated diagnosis. | Add a fitted dark backing panel and text shadow/outline for the core status/objective lines; keep the existing strings, update logic and layout intent. | Native 1280×720 capture over brightest sky, darkest structure and active combat frame; all key status/objective text remains legible, untruncated and inside viewport. |

## Material integration contract

Existing candidates: `/Game/Environment/HarborNine/UpgradePack_20260930/Materials/`, master `M_HNUP_Surface`. Keep source assets and existing material instances intact. Create additive integration instances or a compatible material variant only if additional controls are necessary, then assign them to verified slots. No global replace-by-name.

For the player, read back the current presentation material's full parent graph, original PBR texture bindings and any emissive readability fill before adjusting it. Evaluate that fill independently under the neutral-light test and the final environment; do not remove an existing readability treatment solely because ordinary environment surfaces use zero emission.

Verified imported controls: `BaseColorTex`, `NormalTex`, `ARMTex`, `UVScale`, `Tint`, `MetallicScale`; custom primitive data index 0 = Wetness, index 1 = Corrosion. Albedo is sRGB. Normal and ARM are linear; ARM = R ambient occlusion / G roughness / B metallic. Source normals use DirectX convention; do not flip green again. Default tint is neutral and no emissive brightening is used. Imported master retains source roughness variation and clamps roughness to 0.12–0.98.

Set scale from source metadata and the measured world extent of the assigned mesh. If the UV span is 0–1 and the source tile represents width T cm across a surface width L cm, a starting repeat count is L/T. Inspect the existing UV layout before using that calculation. `UVScale=1` is an import default, not verified texel density.

### Recommended additive controls (proposals, not observed implementation)

Use only when inspection shows the existing master cannot produce the intended result. Preserve current CPD indices. Never darken every surface to compensate for exposure.

| New control | Proposed default/range | Purpose |
|---|---|---|
| `RoughnessBias` | 0; −0.15 to +0.15 | Small adjustment while preserving ARM texture variation. |
| `NormalStrength` | 1; 0.5–1.25 | Correct exaggerated grooves on player-scale surfaces. Use a proper tangent-normal strength function; avoid naïve RGB scaling. |
| `WetDarkening` | 0.12; 0–0.25 | Bounded albedo darkening from a verified wet mask. |
| `WetRoughnessTarget` | 0.22; 0.12–0.40 | Target for wet regions, retaining source variation. |
| `CorrosionMaskTex` | neutral black fallback | Localize rust to physically plausible exposed metal; do not wash all concrete/fabric with rust. |
| `CorrosionRoughness` | 0.85; 0.70–0.95 | Rough oxidized surface response. |
| `CorrosionColor` | sampled from approved authored texture | Avoid baked illumination and arbitrary whole-object color shifts. |

Suggested channel flow: `AO=ARM.r`; `R0=clamp(ARM.g+RoughnessBias,0.12,0.98)`; `M0=saturate(ARM.b*MetallicScale)`. Saturate Wetness/Corrosion inputs. Blend wet response locally; retain some source roughness modulation. For a surface corrosion mask C, blend roughness toward the rust value and reduce metallic toward 0 only in oxidized regions. Painted metal's intact paint is dielectric; bare metal and rust need separate masks. Emissive remains zero for all ordinary surface masters. A lamp lens uses a dedicated emissive material and matching light source.

Instancing constraint: custom primitive data is shared by a primitive component; it must not be treated as a different Wetness value for every instance. If individual instances need independent values, inspect and intentionally add per-instance custom data in a separate material variant while preserving component-level CPD compatibility. Do not create a dynamic material instance per module merely to randomize appearance.

## First integration section: loading lane → warehouse entry

Use an existing route section visible in the dated capture when live access permits locating it. The exact actors, world coordinates and route width have not been observed here; derive them from current source/editor selection and record them in the integration manifest. No guessed transforms.

| Priority | Existing candidate | Assignment/placement intent | Starting response and rejection check |
|---|---|---|---|
| P0 | `MI_HNUP_asphalt_02` | Outdoor loading-lane floor only. Keep stairs/walkway separate. | MetallicScale 0; neutral tint; Wetness 0.05 in covered areas / 0.25 in exposed test area; Corrosion 0. Reject plastic sheen and visibly oversized aggregate. |
| P0 | `MI_HNUP_concrete_wall_003` | Warehouse walls, columns/piers with correct seams. | MetallicScale 0; Wetness 0–0.15; Corrosion 0. Add localized waterline/dirt decals where authored; reject mirror-like concrete. |
| P0 | `MI_HNUP_corrugated_iron_02` | Service-shed cladding and roof spans aligned with corrugation direction. | Keep source ARM metallic mask, MetallicScale 1; Wetness 0.10–0.25. Reject stretched ribs or reversed normals. |
| P0 | `MI_HNUP_blue_metal_plate` | Utility cabinets/generator panel surfaces supported by material slots. | Preserve source masks; MetallicScale 1. Require paint, exposed substrate and corrosion to read distinctly. |
| P1 | Delivered generator + crate + barrel | Generator beside a service zone, crate groups at loading points, a few barrels against functional storage edges. Preserve multi-part node transforms. | Confirm real bounds/pivots, then place. Keep exits, cover lanes, objective access and player clearance intact; retain original collision unless deliberately tested. |
| P1 | Delivered industrial wall lamp | Fix to support/wall at the practical light's source; no floating lights. | Tangent/binormal import warning is unresolved: inspect close-up and repair/reimport before acceptance. Use lamp-specific emissive, not surface albedo brightening. |
| P1 | `MI_HNUP_bicolour_gravel` | Rail ballast / route shoulder beyond traversal lane. | MetallicScale 0; Wetness 0.05–0.15. Reject gravel stretched across vertical surfaces. |
| P1 | `MI_HNUP_weathered_brown_planks` | Timber boards and cargo where geometry supports boards. | MetallicScale 0; Wetness 0–0.10; Corrosion 0. Align grain with plank direction. |
| P2 | `MI_HNUP_brick_wall_10` | Existing masonry subset only; introduce as an architectural zone. | MetallicScale 0; verify brick size and corner transitions before expanding. |
| P2 | `MI_HNUP_denim_fabric` | Backpack/harness fabric slots only after UV/silhouette inspection. | MetallicScale 0; Wetness 0; Corrosion 0. Texture improves fabric surface, not mannequin anatomy. |

The values above are initial art-direction candidates, not measured final calibration. Add detail with deliberate edge wear, drainage streaks, joints, bolts, cable runs and contact grime where the existing modules justify them. Leave enough visual separation for enemies, pickups and interactables. Increase detail first in the chosen section and use it as the reviewed standard for the remaining route.

## Light and HUD implementation notes

Extended exposure semantics matter: with `ExtendDefaultLuminanceRange=True`, the min/max fields are expressed in EV100. Therefore the recorded values 3 and 6 must not be described as a 3×–6× brightness multiplier. For an isolated comparison, override both min/max to the same chosen EV100 and record the effective value. A small bracket such as EV100 4, 6 and 8 is a proposed diagnostic sweep, not a shipping setting. Compare identical camera and sky conditions, then select a measured exposure from the frame/histogram and visual task readability.

Keep imported overcast and sunset HDRIs as alternatives during sky-only calibration. Record the selected cubemap, intensity and rotation; do not switch HDRI and all practical lights in one test. Replace huge overlapping unshadowed fills with a few measured lighting zones only after the fixed exposure test. A proposed first practical bracket is 1,000/3,000/6,000 lumens with a 600–1,200 cm radius for a player-scale local fixture; verify actual units/type and scene scale before applying. Use selective shadows where they establish depth and stop light leaking. Compare cost and appearance on the actual RTX runtime. Atmosphere or fog must not hide missing surface/detail work.

HUD proposal for existing core lines: charcoal panel RGB (0.02, 0.03, 0.04), opacity 0.80, 8 px padding at the 1280×720 reference size, 1–2 px dark text shadow/outline, and existing near-white primary text. Fit backing bounds to measured text and scale with the actual Canvas/viewport convention. Do not append duplicate text, alter objective logic or assume a UMG migration is necessary. Validate text readability directly from native captures; check the composited result instead of quoting the panel's nominal alpha as a contrast proof.

## Original asset brief for Qwen and Codex

Copy this brief when producing original art; generated previews are concept references until the required source files are delivered and imported:

> Create original ZombieTZ Harbor Nine survivor and industrial surface detailing for a damp, overcast coastal logistics yard under progressive infection. Preserve the supplied project's industrial architecture and playable routes. The survivor should read as a working adult with credible proportions, muted olive/charcoal layered utility clothing, weathered woven backpack and harness, scuffed boots and restrained fabric repairs. Avoid a glossy white mannequin finish. Keep the silhouette clear at third-person gameplay distance. Environment detail should show physically plausible rain runoff, concrete pores, seams, chipped painted steel with small exposed-metal areas, localized rust, worn hazard paint, timber grain and ballast. Infection occupies deliberate local clusters and does not replace every surface. Use realistic wear scale, readable roughness and neutral-light albedo with no baked shadows, highlights, lettering or branding. Do not place logos, facial identity references, embedded HUD text or new architecture into texture maps.

Required usable outputs, as applicable:

- Surface assets: seamless original 4096×4096 albedo (sRGB), DirectX tangent normal (linear) and ARM (linear R=AO/G=roughness/B=metallic), plus isolated corrosion/edge-wear masks. Provide real-world tile width/height, source authoring file, channel documentation and provenance/license. A single rendered texture preview is insufficient.
- Survivor: original model/source file, skeleton and bind-pose documentation, animation/retarget compatibility against the actual project's skeleton, skin/clothing/gear material-slot list, texture maps, LODs, skin weights, measured scale and socket fitting notes. Do not claim this exists until a real asset is delivered and checked.
- Codex integration: inspect actual actor/component/material paths and current engine first; retain imported source/master assets; create additive variants; produce a deterministic actor/slot/parameter assignment manifest; preserve existing route/gameplay functions; run the project’s relevant regression checks and package from identified source. Use the current working 5.8.3 toolchain; the earlier 5.8.2 baseline is historical provenance, not a new version gate or a reason to downgrade. Attach these inputs to the existing canonical production handoff rather than creating another task queue.

## Acceptance record per repaired gap

Capture native unretouched images and motion from the packaged build. Record UTC timestamp, host, executable SHA-256, source/package digests, engine version, launch command/profile, resolution, camera transform, mesh/material paths, assignment manifest and relevant runtime log. Use a fixed camera/exposure before/after pair for material/lighting comparison and normal gameplay exposure for playability. Read back installed assets and effective runtime settings separately from source edits. Render settings, asset delivery, successful compile, functional tests and final visual acceptance are separate records.

No final acceptance should be inferred from this specification, the previous 22 passing Python tests, a content directory count, `nanite=candidate`, or the term RTX. Complete one representative section, obtain a source-bound in-motion capture, and extend only the accepted result.

## Evidence and technical references

- `ZombieTZ_visual_diagnosis_20260930.md`, Library ID `libfile_3958293f27e0819194529b7acf656aeb`: source paths, dated capture/build hashes and five verified gaps. Evidence pertains to 30 September only.
- `ZombieTZ_HarborNine_Asset_Delivery.md`, Library ID `libfile_37d7aeb7b1e081919d6089cea66fae5e`: eight surface instances, master/channel/CPD contract, props/HDRIs, import checks and integration boundaries.
- `ZombieTZ_RTX_screenshot.png`, Library ID `libfile_193a14d5f6148191b45899a244089174`: known source capture. Image pixels could not be fetched in this drafting session; visual statements above are attributed to the dated diagnosis.
- [Epic: Auto Exposure](https://dev.epicgames.com/documentation/unreal-engine/auto-exposure-in-unreal-engine): extended EV100 interpretation and fixed min/max exposure.
- [Epic: Physically Based Materials](https://dev.epicgames.com/documentation/unreal-engine/physically-based-materials-in-unreal-engine): base color, roughness and metallic surface response.
- [Epic: Instanced Static Mesh Component](https://dev.epicgames.com/documentation/unreal-engine/instanced-static-mesh-component-in-unreal-engine): instancing and custom-data workflow.

Official technical references checked 4 October 2026. Proposed controls, values, placements and original art direction are authored for this brief and have not been applied to the live project.

## Original concrete asset included in this package

`T_ZombieTZ_HarborConcrete_BaseColor_Candidate.png` is an original AI-generated base-color candidate produced 4 October 2026. Actual dimensions are 1254 × 1254 pixels, RGB PNG, not the requested 4096 × 4096. Import as sRGB and use only as a candidate alongside the existing harbor material. Its neutral-light appearance was visually inspected in the generated preview; seamless repetition, in-engine physical scale and distant mip behavior are not verified. No matching normal, ARM, height map or layered authoring source was generated. This texture is not a complete PBR set and has not been installed on RTX. Prompt asked for orthographic edge-to-edge aged harbor concrete with mineral aggregate, salt erosion, fine cracks, flat diffuse lighting, no highlights, baked shadows, text, logos or border.
