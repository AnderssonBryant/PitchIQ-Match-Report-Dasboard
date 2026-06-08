# PitchIQ | Tactical Match Reports

A football analytics project designed to transform event data into actionable tactical insights through structured post-match reporting.

## Overview

PitchIQ Tactical Match Reports is a post-match analysis framework that evaluates team performance across key phases of play, including:

* In Possession
* Out of Possession
* Offensive Transition
* Defensive Transition

The objective is to provide coaches and analysts with a clear, data-driven understanding of how a team performed beyond traditional match statistics.

Rather than focusing solely on outcomes, PitchIQ emphasizes the underlying processes that drive performance, helping users understand:

* How attacks were built
* How possession was progressed
* How chances were created
* How the team pressed and defended
* How the team performed during transitions

---

## Project Philosophy

Football matches are not won by statistics alone.

PitchIQ is built around a phase-of-play framework that links data to tactical behaviour, allowing analysts to move from:

"What happened?"

to

"Why did it happen?"

and ultimately

"What should happen next?"

---

## Data Source

This project uses publicly available event data from the StatsBomb Open Data repository.

The dataset contains detailed event-level information, including passes, carries, shots, defensive actions, and possession events, which are used to generate the metrics and visualizations presented throughout the dashboard.

StatsBomb Open Data provides an accessible resource for football analytics projects and allows the methodology used in this project to be reproduced and validated by other analysts.

**Source:** https://github.com/statsbomb/open-data

---

## Core Analysis Areas

### In Possession

* Build-Up
* Progression
* Chance Creation

### Out of Possession

* Pressing
* Defensive Organisation
* Ball Recovery

### Offensive Transition

* Counter-Attacking Threat
* Transition Attacks
* Transition Shot Creation

### Defensive Transition

* Counter-Attacks Conceded
* Defensive Recovery
* Transition Vulnerabilities


## Dashboard Structure

### Match Summary

Provides a high-level overview of match performance using key performance indicators.

### In Possession

Focuses on:

* Build-Up
* Ball Progression
* Chance Creation

### Out of Possession

Focuses on:

* Pressing
* Defensive Organization
* Ball Recoveries

### Offensive Transition

Focuses on:

* Counter-Attacking Opportunities
* Transition Entries
* Transition Shot Creation

### Defensive Transition

Focuses on:

* Counter-Attacks Conceded
* Defensive Recovery Actions
* Transition Vulnerabilities

---

## Metrics Included

* Expected Goals (xG)
* Shot Count
* Progressive Passes
* Progressive Carries
* Final Third Entries
* Key Passes
* PPDA
* High Turnovers
* Ball Recoveries
* Transition Attacks
* Transition Shots
* Defensive Recovery Actions

---

## Example Insights

The dashboard enables analysts to identify:

* Progression patterns
* Attacking tendencies
* Pressing effectiveness
* Transition strengths and weaknesses
* Defensive vulnerabilities
* Team performance trends across matches

---

## Project Limitations

Current limitations include:

* Event-data only analysis
* No player-analysis module
* No tracking-data integration
* Limited structural analysis
* No set-piece module

---

## Future Development (Version 2.0)

Planned improvements:

* Player Analysis Module
* Possession Chain Analysis
* Team Structure Analysis
* Automated Match Reporting
* Enhanced Phase-of-Play Analysis
* Set-Piece Analysis
