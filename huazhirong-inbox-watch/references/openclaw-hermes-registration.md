# OpenClaw / Hermes 注册（inbox-watch）

```bash
git clone https://github.com/zhou256bug/AI-Agent-Skills.git ~/Projects/AI-Agent-Skills
```

Skill 路径：`~/Projects/AI-Agent-Skills/huazhirong-inbox-watch/`

## OpenClaw

```json5
{
  skills: {
    load: { extraDirs: ["~/Projects/AI-Agent-Skills"], watch: true },
    entries: { "huazhirong-inbox-watch": { enabled: true } },
  },
}
```

## Hermes

```yaml
skills:
  external_dirs:
    - ~/Projects/AI-Agent-Skills
```

slash：`/inbox-watch`（见 `bundles/inbox-watch.hermes.yaml`）

```bash
hermes chat --toolsets terminal,skills -q "/inbox-watch 扫描未读邮件"
```

## Cron

见 `references/cron-setup.md` 与 `references/agent-cron-prompt.md`。

## 首次配置

```bash
python3 huazhirong-inbox-watch/scripts/inbox_watch_cli.py setup status
python3 huazhirong-inbox-watch/scripts/inbox_watch_cli.py setup apply --verify
```

源文件：`agents/{openclaw,hermes,openai}.yaml`
