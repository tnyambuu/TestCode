# Project Parallelism Flow - Mermaid Diagram

## Architecture Overview

```mermaid
graph TB
    %% Client Layer
    subgraph "Client Layer"
        B1[Browser 1<br/>WebSocket]
        B2[Browser 2<br/>WebSocket]
        B3[Browser 3<br/>WebSocket]
        B4[Browser N<br/>WebSocket]
    end

    %% Django Application Layer
    subgraph "Django Application Layer"
        subgraph "Django Channels (ASGI)"
            C1[ChatConsumer<br/>Room: chat_1]
            C2[ChatConsumer<br/>Room: chat_2]
            C3[ChatConsumer<br/>Room: chat_3]
        end
        
        subgraph "Django REST API"
            API[TestProcess View<br/>• File Upload<br/>• Task Dispatch<br/>• Return Task IDs]
        end
    end

    %% Redis Layer
    subgraph "Redis Infrastructure"
        subgraph "Redis 6380 - Celery"
            RB[Celery Broker<br/>Task Queue]
            RR[Result Backend<br/>Task Results]
        end
        
        subgraph "Redis 6379 - Channels"
            CL[Channel Layer<br/>WebSocket Groups<br/>chat_room1, chat_room2...]
        end
        
        subgraph "Redis 6381 - Cache"
            CACHE[Django Cache]
        end
    end

    %% Celery Worker Layer
    subgraph "Celery Worker Layer"
        subgraph "Worker 1"
            W1[test_process Task<br/>PID: 1234<br/>Process: Worker-1]
        end
        
        subgraph "Worker 2"
            W2[test_process Task<br/>PID: 5678<br/>Process: Worker-2]
        end
        
        subgraph "Worker 3"
            W3[test_process Task<br/>PID: 9012<br/>Process: Worker-3]
        end
        
        subgraph "Worker N"
            WN[test_process Task<br/>PID: 3456<br/>Process: Worker-N]
        end
    end

    %% Connections
    B1 -.->|WebSocket| C1
    B2 -.->|WebSocket| C2
    B3 -.->|WebSocket| C3
    B4 -.->|WebSocket| C1

    API -->|Task Dispatch| RB
    RB -->|Task Distribution| W1
    RB -->|Task Distribution| W2
    RB -->|Task Distribution| W3
    RB -->|Task Distribution| WN

    W1 -->|Results| RR
    W2 -->|Results| RR
    W3 -->|Results| RR
    WN -->|Results| RR

    W1 -.->|Real-time Updates| CL
    W2 -.->|Real-time Updates| CL
    W3 -.->|Real-time Updates| CL
    WN -.->|Real-time Updates| CL

    CL -.->|Broadcast Updates| C1
    CL -.->|Broadcast Updates| C2
    CL -.->|Broadcast Updates| C3

    C1 -.->|WebSocket Response| B1
    C2 -.->|WebSocket Response| B2
    C3 -.->|WebSocket Response| B3
    C1 -.->|WebSocket Response| B4

    API -->|Cache Operations| CACHE
```

## Task Execution Flow

```mermaid
sequenceDiagram
    participant Client as Browser Client
    participant API as Django REST API
    participant Redis as Redis Broker
    participant Worker as Celery Worker
    participant WS as WebSocket Channel
    participant Room as Chat Room

    Client->>API: POST /server/test-process/<br/>Upload multiple files
    API->>Redis: Dispatch tasks to queue
    API->>Client: Return task IDs
    
    loop For each file
        Redis->>Worker: Assign task to worker
        Worker->>WS: Send "Started" update
        WS->>Room: Broadcast to room
        Room->>Client: Real-time progress update
        
        loop 10 iterations (simulating processing)
            Worker->>Worker: Process file (1 second)
            Worker->>WS: Send progress update
            WS->>Room: Broadcast progress
            Room->>Client: Real-time progress update
        end
        
        Worker->>WS: Send "Completed" update
        WS->>Room: Broadcast completion
        Room->>Client: Final progress update
        Worker->>Redis: Store task result
    end
```

## Parallel Processing Details

```mermaid
graph LR
    subgraph "File Upload Process"
        F1[File 1.pdf]
        F2[File 2.pdf]
        F3[File 3.pdf]
        F4[File N.pdf]
    end
    
    subgraph "Task Creation"
        T1[Task 1<br/>test_process.delay]
        T2[Task 2<br/>test_process.delay]
        T3[Task 3<br/>test_process.delay]
        T4[Task N<br/>test_process.delay]
    end
    
    subgraph "Worker Execution"
        subgraph "Worker Process 1"
            W1[test_process<br/>PID: 1234<br/>File: 1.pdf<br/>Room: chat_1]
        end
        
        subgraph "Worker Process 2"
            W2[test_process<br/>PID: 5678<br/>File: 2.pdf<br/>Room: chat_1]
        end
        
        subgraph "Worker Process 3"
            W3[test_process<br/>PID: 9012<br/>File: 3.pdf<br/>Room: chat_1]
        end
        
        subgraph "Worker Process N"
            WN[test_process<br/>PID: 3456<br/>File: N.pdf<br/>Room: chat_1]
        end
    end
    
    subgraph "Real-time Updates"
        WS[WebSocket Channel<br/>chat_1]
        CLIENT[Connected Clients<br/>Multiple Browsers]
    end
    
    F1 --> T1
    F2 --> T2
    F3 --> T3
    F4 --> T4
    
    T1 --> W1
    T2 --> W2
    T3 --> W3
    T4 --> WN
    
    W1 -.->|Progress Updates| WS
    W2 -.->|Progress Updates| WS
    W3 -.->|Progress Updates| WS
    WN -.->|Progress Updates| WS
    
    WS -.->|Broadcast| CLIENT
```

## Redis Infrastructure

```mermaid
graph TB
    subgraph "Redis Infrastructure"
        subgraph "Redis 6380 - Celery Operations"
            direction TB
            RB[Celery Broker<br/>• Task Queue<br/>• Message Routing<br/>• Load Balancing]
            RR[Result Backend<br/>• Task Results<br/>• Status Tracking<br/>• Result Storage]
        end
        
        subgraph "Redis 6379 - WebSocket Channels"
            direction TB
            CL[Channel Layer<br/>• WebSocket Groups<br/>• chat_room1, chat_room2<br/>• Real-time Broadcasting<br/>• Message Persistence]
        end
        
        subgraph "Redis 6381 - Django Cache"
            direction TB
            CACHE[Django Cache<br/>• Session Storage<br/>• Template Caching<br/>• Query Result Cache<br/>• Performance Optimization]
        end
    end
    
    subgraph "Configuration"
        CONFIG[Redis Settings<br/>• Port 6380: Celery<br/>• Port 6379: Channels<br/>• Port 6381: Cache<br/>• Capacity: 2000 messages<br/>• Expiry: 1800 seconds]
    end
```

## Key Features

### 🔄 **Parallel Processing**
- Multiple files processed simultaneously
- Each file gets its own Celery task
- Tasks distributed across multiple workers
- Process-level isolation for fault tolerance

### 📡 **Real-time Communication**
- WebSocket connections for live updates
- Progress broadcasting to all connected clients
- Asynchronous task-to-client communication
- Room-based message routing

### ⚙️ **Scalability**
- Horizontal scaling with multiple workers
- Redis-based message brokering
- Load balancing across worker processes
- Fault tolerance with task retry mechanisms

### 🛠️ **Configuration**
- **Celery**: 6 tasks per worker, 1200s time limit
- **Redis**: Separate instances for different purposes
- **WebSocket**: 2000 message capacity, 1800s expiry
- **Multiprocessing**: Process isolation and monitoring
