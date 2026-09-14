# Bank / hybrid / cloud-brain

| Mode | Pixels | LLM | Default for |
|---|---|---|---|
| bank | Worker disk only | Local | Core banking UAT |
| hybrid | Worker disk; labels may leave | Customer Azure OpenAI | Mid-market |
| cloud-brain | Cropped frames to Control | Opt-in | Non-regulated |

`LIQA_BRAIN_MODE=local|hybrid|cloud` on the Worker. Bank mode refuses Cursor dispatch of screenshots.
