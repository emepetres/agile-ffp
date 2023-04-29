# agile-ffp

Build agile charts for firm fixed price projects, to compute estimated milestones deadlines.

## Features

- [x] CLI tool to create Gantt from yaml
- [ ] Support priority between tasks
- [ ] Support for vacations low capacity
- [ ] Export to CSV

## Usage

`python -m src.agileffp.main -f sample.yml`

### Format yml file

```yaml
capacity:
  team1:
    members: 2
    starts: 2023-04-17
  team2:
    members: 2
    starts: 2023-05-15
    ends: 2025-12-31
  ...

tasks:
  - name: task1
    estimate:
      research: 25
      web: 30
  - name: task2
    estimate:
      research: 100
      web: 100
    depends_on:
      - task1
  - name: task2
    estimate:
      web:
        effort: 50
        max_capacity: 1
    depends_on:
      - task1
```
