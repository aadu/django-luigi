# Django-Luigi
## Features
- Task history
- Model update tracking
- Scheduling via Celery
- Interrogate luigi tasks
- Job Model

## Advantages of Luigi Integration
- Idempotency
- Pruning
- Automatically invoke dependencies
- Task Graph

## Jobs
- A job represents a top-level luigi task
- In other words, a job always has a luigi task associated with it
- A job also is associated with a celery task that runs/manages it.

### State
- Queued
- Pending
- Started
- Resolving Dependencies
- Waiting for Resource
- Running
- Failed
- Revoked
- Completed
<!--
state
state_updated
host
-->
- Pending
- 







# Add abstraction layer using workers as resources
# 
# Workers as resources
# 
# Add Scheduler
# Integrate Persistent Database
# Resource Queue
class ResourceMap:
    pass


class Worker



chain(a, b, c)


task.run()
task.requires()

Scheduler and Queue for Luigi

# Concept:

A Job has an associated task
The same type of task may have different jobs associated with it because a task doesn't need to know about it's job, just the inverse.
A job is a request from the user for something.
States:
- activately processing task A, 34 tasks remaining
- waiting for resource B before continuing, 4 other jobs with priority for resource B
- failed -- Task A failure caused by upstream task C failure


# Problems:
- Job state in Database
- Failed clusters 

CACHING
# Instant lookup of job status


# STATES