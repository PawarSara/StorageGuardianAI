# Storage Guardian AI

Storage Guardian AI is a context-aware intelligent storage management system designed to optimize the lifecycle of personal files safely.

## Problem Statement

When laptop storage becomes full, users often do not know which personal files are safe to remove, archive, or offload.

Traditional storage cleanup systems primarily rely on categories and simple signals such as file size, age, temporary files, or duplicate detection.

Storage Guardian AI analyzes file usage context to estimate the current local relevance of personal files.

## Core Idea

The system does not assume that an old or inactive file is unimportant.

Instead, it analyzes:

- File metadata
- Modification activity
- Recent file activity
- Exact duplicate evidence
- Folder context
- Active project relationships

The system estimates the current local relevance of a file.

Local relevance is different from personal or emotional importance.

## Current Pipeline

Personal Files
↓
File Scanner
↓
Metadata Collection
↓
Activity Tracking
↓
Exact Duplicate Detection
↓
Unified Feature Engine
↓
Folder Context Detection
↓
Project Relationship Detection
↓
Local Relevance Analysis
↓
User-Assisted Label Collection
↓
ML Training Dataset

## Implemented Phases

1. File Scanner
2. Metadata Storage
3. File Activity Tracking
4. Exact Duplicate Detection
5. Duplicate Context Analysis
6. Unified File Feature Engine
7. Folder Context Detection
8. Active Project Relationship Detection
9. Rule-Based Relevance Baseline
10. Real File Relevance Label Collection

## Current ML Features

The current feature pipeline collects:

- File size
- File extension
- File age
- Days since modification
- Modification count
- Recent activity count
- Duplicate status
- Duplicate count
- Folder type
- Project score
- Recent project file count
- Active project status

## ML Target

The ML model will predict:

- HIGH local relevance
- MEDIUM local relevance
- LOW local relevance

Low local relevance does not mean that a file is unimportant or safe to delete.

## Safety Principle

The ML model will not directly perform permanent deletion.

A separate lifecycle safety controller will consider:

- Duplicate evidence
- Cloud recoverability
- Secondary storage availability
- Network condition
- Storage pressure

Irreversible or uncertain actions will require user approval.

## Technology Stack

- Python
- Watchdog
- Pandas
- Machine Learning
- Windows File System
- Cloud Storage APIs

## Project Status

Phase 1 to Phase 10 completed.

Current focus: real labelled dataset collection and machine learning pipeline development.