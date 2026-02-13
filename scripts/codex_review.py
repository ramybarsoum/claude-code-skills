#!/usr/bin/env python3
"""
Multi-Purpose Review via OpenRouter (Feb 2026)

Usage:
    python scripts/codex_review.py --file src/utils/fileParser.ts --type code
    python scripts/codex_review.py --file backend/app/routers/auth.py --type security
    python scripts/codex_review.py --file docs/ARCHITECTURE.md --type plan
    python scripts/codex_review.py --dir src/components --max-files 5
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    os.system("pip install httpx")
    import httpx

# Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_TOKENS = 4000

# =============================================================================
# REVIEW TYPES with optimized models (Feb 2026)
# =============================================================================

REVIEW_TYPES = {
    "code": {
        "name": "Code Review",
        "temperature": 0.3,
        "recommended": "mimo-v2",
        "models": {
            # === FREE ===
            "mimo-v2": "xiaomi/mimo-v2-flash:free",              # #1 SWE-bench (EMPFOHLEN)
            "devstral": "mistralai/devstral-2512:free",          # Agentic Coding Spezialist
            "deepseek-r1": "deepseek/deepseek-r1-0528:free",    # DeepSeek R1 reasoning
            "r1-chimera": "tngtech/deepseek-r1t2-chimera:free", # R1 Chimera variant
            "qwen3-coder": "qwen/qwen3-coder:free",             # 480B MoE Code-Gen
            "gpt-oss": "openai/gpt-oss-120b:free",              # OpenAI open-weight
            # === PAID (Feb 2026) ===
            "codex-5.2": "openai/gpt-5.2-codex",                # $0.0018/1K - OpenAI Codex
            "codex-5.3": "openai/gpt-5.3-codex",                # API-Rollout Feb 2026
            "codestral": "mistralai/codestral-2508",             # $0.0003/1K - Mistral code specialist
            "qwen-coder": "qwen/qwen3-coder-plus",              # $0.0010/1K - Qwen3 Coder+
            "deepseek-v3": "deepseek/deepseek-v3.2",            # $0.0003/1K - DeepSeek latest
        }
    },
    "security": {
        "name": "Security Review",
        "temperature": 0.2,
        "recommended": "deepseek-r1",
        "models": {
            # === FREE ===
            "deepseek-r1": "deepseek/deepseek-r1-0528:free",    # Reasoning (EMPFOHLEN)
            "r1-chimera": "tngtech/deepseek-r1t2-chimera:free", # R1 Chimera variant
            "llama-405b": "meta-llama/llama-3.1-405b-instruct:free",  # Groesstes Open-Source
            # === PAID (Feb 2026) ===
            "codex-5.2": "openai/gpt-5.2-codex",                # $0.0018/1K - OpenAI Codex
            "codex-5.3": "openai/gpt-5.3-codex",                # API-Rollout Feb 2026
            "gemini-3-pro": "google/gemini-3-pro-preview",       # $0.002/1K - Google Gemini 3 Pro
            "gemini-2.5-pro": "google/gemini-2.5-pro",           # $0.0013/1K - Gemini 2.5 Pro
            "o3": "openai/o3",                                   # $0.002/1K - OpenAI o3 reasoning
            "o3-deep": "openai/o3-deep-research",                # $0.01/1K - Deep security analysis
        }
    },
    "plan": {
        "name": "Plan/Architecture Review",
        "temperature": 0.4,
        "recommended": "deepseek-r1",
        "models": {
            # === FREE ===
            "deepseek-r1": "deepseek/deepseek-r1-0528:free",    # Best reasoning (EMPFOHLEN)
            "r1-chimera": "tngtech/deepseek-r1t2-chimera:free", # R1 Chimera variant
            "thinking": "liquid/lfm-2.5-1.2b-thinking:free",    # Liquid thinking model
            "gpt-oss": "openai/gpt-oss-120b:free",              # OpenAI open-weight
            "llama-405b": "meta-llama/llama-3.1-405b-instruct:free",  # Groesstes Open-Source
            # === PAID (Feb 2026) ===
            "codex-5.2": "openai/gpt-5.2-codex",                # $0.0018/1K - OpenAI Codex
            "codex-5.3": "openai/gpt-5.3-codex",                # API-Rollout Feb 2026
            "o3": "openai/o3",                                   # $0.002/1K - OpenAI o3
            "o4-mini": "openai/o4-mini-deep-research",           # $0.002/1K - OpenAI o4-mini
            "gemini-3-pro": "google/gemini-3-pro-preview",       # $0.002/1K - Gemini 3 Pro
            "kimi-thinking": "moonshotai/kimi-k2-thinking",      # $0.0004/1K - Moonshot Kimi
        }
    }
}

DEFAULT_TYPE = "code"

# =============================================================================
# MODEL ALIASES (resolve common name variants)
# =============================================================================

MODEL_ALIASES = {
    "codex": "codex-5.2",
    "gpt-5.2-codex": "codex-5.2",
    "gpt-5.3-codex": "codex-5.3",
    "gpt-5-codex": "codex-5",
    "gpt-5.1-codex-max": "codex-5.1-max",
    "mimo": "mimo-v2",
    "qwen-coder": "qwen3-coder",
}

# =============================================================================
# BEST MODEL per type (for --best / --best-free flags)
# =============================================================================

BEST_PAID = {"code": "codex-5.2", "security": "o3", "plan": "o3"}
BEST_FREE = {"code": "mimo-v2", "security": "deepseek-r1", "plan": "deepseek-r1"}

# Load API key from environment or .env files
def get_api_key() -> str:
    """Load OpenRouter API key from environment or .env files."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key

    # Try common .env file locations
    env_files = [
        Path(__file__).parent.parent / ".env.local",
        Path(__file__).parent.parent / ".env",
        Path.home() / ".openrouter",
    ]

    for env_file in env_files:
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("OPENROUTER_API_KEY="):
                        return line.split("=", 1)[1].strip()

    raise ValueError(
        "OPENROUTER_API_KEY not found. Set it via:\n"
        "  - Environment variable: export OPENROUTER_API_KEY=sk-or-...\n"
        "  - .env.local file: OPENROUTER_API_KEY=sk-or-...\n"
        "  - ~/.openrouter file: OPENROUTER_API_KEY=sk-or-..."
    )


# =============================================================================
# SYSTEM PROMPTS per review type
# =============================================================================

SYSTEM_PROMPTS = {
    "code": """You are an expert code reviewer. Analyze the code for:

## Review Focus Areas

### 1. Security (CRITICAL)
- OWASP Top 10 vulnerabilities
- Injection risks (SQL, NoSQL, Command)
- XSS vulnerabilities
- Hardcoded secrets
- Input validation gaps
- Auth/AuthZ issues

### 2. Performance
- N+1 query patterns
- Memory leaks
- Unnecessary operations
- Async/await anti-patterns
- Missing caching opportunities

### 3. Maintainability
- DRY violations
- SOLID principle violations
- High cyclomatic complexity
- Missing error handling
- Poor naming conventions

### 4. Type Safety
- Unsafe type usage (any, unknown)
- Missing type annotations
- Type narrowing issues

## Output Format

```markdown
## Code Review Summary

**Risk Level**: [LOW | MEDIUM | HIGH | CRITICAL]
**Lines Reviewed**: X

### Critical Issues (MUST FIX)
1. [Issue] - Line X: Description
   - Impact: ...
   - Fix: ...

### Improvements (SHOULD FIX)
1. ...

### Minor Suggestions (COULD FIX)
1. ...

### Positive Aspects
- ...
```

Be specific, cite line numbers, provide actionable fixes.""",

    "security": """You are an expert security auditor. Perform a comprehensive security review.

## Security Review Checklist

### 1. OWASP Top 10 (2025)
- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection (SQL, NoSQL, OS, LDAP)
- [ ] A04: Insecure Design
- [ ] A05: Security Misconfiguration
- [ ] A06: Vulnerable Components
- [ ] A07: Auth Failures
- [ ] A08: Data Integrity Failures
- [ ] A09: Logging Failures
- [ ] A10: SSRF

### 2. Secret Detection
- API keys, tokens, passwords
- Connection strings
- Private keys, certificates
- Environment-specific secrets

### 3. Input Validation
- SQL/NoSQL injection vectors
- XSS (stored, reflected, DOM)
- Path traversal
- Command injection
- SSRF vectors

### 4. Authentication & Authorization
- Session management
- Token handling (JWT, OAuth)
- RBAC/ABAC implementation
- Privilege escalation risks

### 5. Data Protection
- PII handling
- Encryption at rest/transit
- GDPR/DSGVO compliance

## Output Format

```markdown
## Security Review Report

**Overall Risk**: [LOW | MEDIUM | HIGH | CRITICAL]
**CVSS Score Estimate**: X.X

### Critical Vulnerabilities
1. **[CVE-like ID]** - Line X
   - Type: [Injection/XSS/etc]
   - Severity: CRITICAL
   - Description: ...
   - Exploit Scenario: ...
   - Remediation: ...

### High Severity Issues
...

### Medium Severity Issues
...

### Low Severity / Informational
...

### Security Posture Summary
- Strengths: ...
- Weaknesses: ...
- Recommendations: ...
```

Be thorough. Assume adversarial input. Cite specific line numbers.""",

    "plan": """You are an expert software architect. Review this plan/architecture document.

## Architecture Review Criteria

### 1. Completeness
- Are all requirements addressed?
- Are edge cases considered?
- Are error scenarios handled?
- Are rollback strategies defined?

### 2. Feasibility
- Is the timeline realistic?
- Are dependencies identified?
- Are resource requirements clear?
- Are technical constraints addressed?

### 3. Scalability
- Will it handle 10x load?
- Are bottlenecks identified?
- Is horizontal scaling possible?
- Are caching strategies defined?

### 4. Maintainability
- Is the design modular?
- Are interfaces well-defined?
- Is the complexity justified?
- Is documentation sufficient?

### 5. Risk Assessment
- What could go wrong?
- What are the dependencies?
- What's the blast radius?
- What's the recovery plan?

## Output Format

```markdown
## Architecture Review

**Recommendation**: [APPROVE | APPROVE_WITH_CHANGES | NEEDS_REWORK | REJECT]
**Confidence**: [HIGH | MEDIUM | LOW]

### Strengths
- ...

### Concerns
1. **[Area]**: Description
   - Risk: ...
   - Suggestion: ...

### Missing Elements
- ...

### Alternative Approaches
1. **[Approach]**: Description
   - Pros: ...
   - Cons: ...
   - When to use: ...

### Questions for Clarification
1. ...

### Go/No-Go Recommendation
...
```

Think critically. Challenge assumptions. Suggest alternatives."""
}


def read_file(file_path: str) -> tuple[str, str]:
    """Read file and return (content, extension)"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding="utf-8")
    return content, path.suffix


def read_directory(dir_path: str, max_files: int = 5) -> list[tuple[str, str]]:
    """Read multiple files from directory"""
    path = Path(dir_path)
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    extensions = {".ts", ".tsx", ".py", ".js", ".jsx"}
    files = []

    for file in sorted(path.rglob("*")):
        if file.suffix in extensions and "node_modules" not in str(file):
            try:
                content = file.read_text(encoding="utf-8")
                files.append((str(file), content))
                if len(files) >= max_files:
                    break
            except Exception:
                continue

    return files


def call_review_api(
    content: str,
    filename: str,
    review_type: str = DEFAULT_TYPE,
    model_key: Optional[str] = None,
    focus: Optional[str] = None,
) -> str:
    """Call OpenRouter API with review-type-specific model and prompt."""
    api_key = get_api_key()

    # Get review type config
    type_config = REVIEW_TYPES.get(review_type, REVIEW_TYPES[DEFAULT_TYPE])
    models = type_config["models"]

    # Use specified model or recommended default
    if model_key is None:
        model_key = type_config["recommended"]
    model_key = MODEL_ALIASES.get(model_key, model_key)

    model = models.get(model_key)
    if not model:
        # Try to find model across all types
        for rt in REVIEW_TYPES.values():
            if model_key in rt["models"]:
                model = rt["models"][model_key]
                break
        if not model:
            raise ValueError(f"Unknown model: {model_key}. Available for {review_type}: {list(models.keys())}")

    # Build user message
    focus_instruction = f"\n\n**Primary Focus**: {focus}" if focus else ""
    user_message = f"""Review this {'document' if review_type == 'plan' else 'code'} from `{filename}`:{focus_instruction}

```
{content}
```"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS[review_type]},
            {"role": "user", "content": user_message},
        ],
        "temperature": type_config["temperature"],
        "max_tokens": MAX_TOKENS,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Svenja-dev/claude-code-skills",
        "X-Title": "Claude Code Review Skill",
    }

    with httpx.Client(timeout=180.0) as client:
        response = client.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()

    result = response.json()

    if "choices" not in result or len(result["choices"]) == 0:
        raise ValueError(f"Unexpected API response: {result}")

    return result["choices"][0]["message"]["content"]


def list_models(review_type: Optional[str] = None) -> None:
    """Print available models for given review type or all types."""
    types_to_show = [review_type] if review_type else REVIEW_TYPES.keys()

    for rt in types_to_show:
        if rt not in REVIEW_TYPES:
            continue
        config = REVIEW_TYPES[rt]
        print(f"\n=== {config['name']} ===")
        print(f"Recommended: {config['recommended']}")
        print("Models:")
        for name, model_id in config["models"].items():
            marker = " (EMPFOHLEN)" if name == config["recommended"] else ""
            free = " [FREE]" if ":free" in model_id else ""
            print(f"  {name}: {model_id}{free}{marker}")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Purpose Review via OpenRouter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python codex_review.py --file src/app.ts --type code
  python codex_review.py --file auth.py --type security --model o3
  python codex_review.py --file ARCHITECTURE.md --type plan
  python codex_review.py --list-models
  python codex_review.py --list-models --type security

Author: Svenja-dev (github.com/Svenja-dev)
Repository: https://github.com/Svenja-dev/claude-code-skills
"""
    )

    parser.add_argument("--file", "-f", help="File to review")
    parser.add_argument("--dir", "-d", help="Directory to review")
    parser.add_argument("--max-files", type=int, default=5, help="Max files from directory")
    parser.add_argument(
        "--type", "-t",
        choices=list(REVIEW_TYPES.keys()),
        default=DEFAULT_TYPE,
        help=f"Review type (default: {DEFAULT_TYPE})",
    )
    parser.add_argument(
        "--focus",
        help="Additional focus area (e.g., 'authentication', 'performance')",
    )
    parser.add_argument("--model", "-m", help="Model to use (see --list-models)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--list-models", "-l", action="store_true", help="List available models")
    parser.add_argument("--best", action="store_true",
        help="Use best paid model per review type")
    parser.add_argument("--best-free", action="store_true",
        help="Use best free model per review type")

    args = parser.parse_args()

    # List models mode
    if args.list_models:
        list_models(args.type if args.type != DEFAULT_TYPE else None)
        return

    if not args.file and not args.dir:
        parser.error("Either --file or --dir is required (or use --list-models)")

    results = []
    type_config = REVIEW_TYPES[args.type]
    if args.best:
        model_key = BEST_PAID.get(args.type, type_config["recommended"])
    elif args.best_free:
        model_key = BEST_FREE.get(args.type, type_config["recommended"])
    else:
        model_key = args.model or type_config["recommended"]
    model_key = MODEL_ALIASES.get(model_key, model_key)

    try:
        # Resolve model name
        model_id = type_config["models"].get(model_key)
        if not model_id:
            for rt in REVIEW_TYPES.values():
                if model_key in rt["models"]:
                    model_id = rt["models"][model_key]
                    break

        print(f"Review Type: {type_config['name']}", file=sys.stderr)
        print(f"Model: {model_key} ({model_id or 'unknown'})", file=sys.stderr)
        print("-" * 50, file=sys.stderr)

        if args.file:
            content, ext = read_file(args.file)
            print(f"Reviewing {args.file} ({len(content)} chars)...", file=sys.stderr)
            review = call_review_api(
                content, args.file, args.type, model_key,
                args.focus if args.focus else None
            )
            results.append({"file": args.file, "type": args.type, "model": model_key, "review": review})

        elif args.dir:
            files = read_directory(args.dir, args.max_files)
            print(f"Reviewing {len(files)} files from {args.dir}...", file=sys.stderr)

            for filepath, content in files:
                print(f"  - {filepath}...", file=sys.stderr)
                review = call_review_api(
                    content, filepath, args.type, model_key,
                    args.focus if args.focus else None
                )
                results.append({"file": filepath, "type": args.type, "model": model_key, "review": review})

        # Output
        if args.json:
            output = json.dumps(results, indent=2, ensure_ascii=False)
        else:
            output_parts = []
            for r in results:
                header = f"# {type_config['name']}: {r['file']}\n**Model**: {r['model']}\n"
                output_parts.append(f"{header}\n{r['review']}\n")
            output = "\n---\n\n".join(output_parts)

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"\nReview saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 402:
            print(f"Error: Payment required. Model '{model_key}' needs credits.", file=sys.stderr)
            print("Use a free model or add credits at https://openrouter.ai/credits", file=sys.stderr)
        else:
            print(f"HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
