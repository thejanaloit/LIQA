# Smoke-test LIQA MCP modules (portable)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$env:LIQA_HOME = $Root
if (-not $env:LIQA_AGENCY_HOME) {
  $cand = Join-Path (Split-Path $Root -Parent) "agency-agents"
  if (Test-Path $cand) { $env:LIQA_AGENCY_HOME = $cand }
  elseif (Test-Path "E:\agency-agents") { $env:LIQA_AGENCY_HOME = "E:\agency-agents" }
  else { $env:LIQA_AGENCY_HOME = $Root }
}
$env:PYTHONPATH = Join-Path $Root "mcp"

py -3 -c @"
import json, sys, os
sys.path.insert(0, os.path.join(r'$Root', 'mcp'))
os.environ['LIQA_HOME'] = r'$Root'
import agency_mesh, learner_speed, resource_map, engineer_persona, laws, book1_contract, flow
from paths import REPO_ROOT, WORKSPACE
print('persona', engineer_persona.PERSONA_NAME, engineer_persona.PERSONA_VERSION)
print('laws', laws.VERSION, 'phases', len(laws.ISTQB_PHASES))
print('agency', agency_mesh.list_specialists(limit=5)['count'], agency_mesh.list_specialists(limit=5).get('source'))
print('learn', learner_speed.suggest(task_key='PF-55248')['ok'])
print('resources', resource_map.map_resources()['ok'])
print('book1_cols', len(book1_contract.BOOK1_COLUMNS))
flow.ensure_workspace()
src = open(os.path.join(r'$Root', 'mcp', 'server.py'), encoding='utf-8').read()
assert src.count('def liqa_') >= 70
print(json.dumps({'ok': True, 'product': 'LIQA', 'home': str(REPO_ROOT), 'tools': src.count('def liqa_')}, indent=2))
"@
