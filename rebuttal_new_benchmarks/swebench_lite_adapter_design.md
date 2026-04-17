# SWE-bench Lite Adapter Design

> Status: NOT STARTED
> Blocker: Adapter implementation required before any experiments
> Estimated effort: 1-2 weeks

## Overview

SWE-bench Lite is a curated subset of 300 real-world GitHub issues from popular Python repos.
Each instance: issue description → code patch → test verification.

## BaseEnv Interface Mapping

| BaseEnv Method | SWE-bench Implementation |
|---|---|
| `reset(seed)` | Load instance: clone repo at base commit, parse issue |
| `step(action_int)` | Apply code edit action, run test subset |
| `get_state()` | Git snapshot: `git stash` or commit hash + diff |
| `set_state(state)` | `git checkout` + `git apply` |
| `get_actions()` | Discrete action set: file targets × edit types |
| `get_text_description()` | Issue text + relevant file contents + test output |
| `forward_value(action)` | Heuristic: syntax check + partial test pass rate |
| `is_success(reward, terminated, info)` | All relevant tests pass |
| `classify_state()` | Phase: "localization" / "editing" / "verification" |
| `make_state_key()` | Hash of current diff |
| `get_signals()` | See signal list below |

## Signals for Direction Discovery

```python
def get_signals(self):
    return {
        "step_count": self._step_count,
        "token_entropy": self._last_entropy,        # from proposer
        "num_files_touched": len(self._modified_files),
        "patch_size_lines": self._patch_line_count,
        "test_pass_rate": self._current_pass_rate,   # 0.0 - 1.0
        "has_syntax_error": int(self._syntax_error),
        "num_test_failures": self._num_failing_tests,
        "issue_length": self._issue_token_count,
        "repo_familiarity": self._files_seen_ratio,  # files read / total
    }
```

## Action Space Design

Option A (simpler, recommended): Free-form code generation like APPS
- Agent generates full patch text at each step
- Action space: [0] = apply current patch, [1] = request more context, [2] = run tests
- Rollout: K-variant patch generation (temp=0.7, K=5)

Option B (structured): Discrete file-level actions
- Agent selects file → edit location → edit content
- More structured but harder to implement

**Recommend Option A** — closest to existing `apps_env.py` pattern.

## Dependencies

```
pip install swebench
# Docker required for sandboxed test execution
docker pull ghcr.io/princeton-nlp/swe-agent:latest
```

## Key Challenges

1. **Test execution isolation**: Need Docker or subprocess sandboxing
2. **Long instance solve times**: Some instances take 10+ minutes
3. **Variable difficulty**: Pass@1 ranges from 3% to 45% across models
4. **State management**: Full repo state is expensive to snapshot

## Reference Files

- `frvc/envs/apps_env.py` — most similar existing adapter (code gen)
- `frvc/envs/intercode_bash_env.py` — interactive shell pattern
- `frvc/envs/base.py` — abstract interface definition
- `frvc/envs/registry.py` — where to register the new adapter
