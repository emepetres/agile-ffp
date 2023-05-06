# agile-ffp

Build agile charts for firm fixed price projects, to compute estimated milestones deadlines.

## Features

- [x] CLI tool to create Gantt from yaml
- [x] Support priority between tasks
- [x] Support for vacations low capacity
- [x] Export to CSV

## Usage

CLI:
`python -m src.agileffp.main -f sample.yml`

SERVER:
`cd src && python -m flask --app agileffp run --debug`
Then go to _localhost:5000/gantt_

### Sample yml file

This sample represents the espected schema of the yaml file

```yaml
capacity:
  team1:
    members: 2
    starts: 2023-04-17
    vacation_months:
      - 7
      - 8
  team2:
    members: 2
    starts: 2023-05-15
    ends: 2025-12-31
    exceptions:
      - members: 1
        starts: 2023-05-15
        ends: 2023-06-03
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
    priority: 50 # [0 - 99]
    depends_on:
      - task1
```
