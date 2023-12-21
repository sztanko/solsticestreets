[
    {
        "name": "solsticestreets-prod",
        "image": "sztanko/solsticestreets_prod",
        "essential": true,
        "command": [
            "/bin/bash",
            "-c",
            "./run.sh config/settings.planet.sh"
        ],
        "mountPoints": [
            {
                "containerPath": "/data",
                "sourceVolume": "data"
            }
        ],
        "secrets": [
            {
                "name": "GIT_TOKEN",
                "valueFrom": "${SECRET_ARN}:GIT_TOKEN::"
            },
            {
                "name": "TG_BOT",
                "valueFrom": "${SECRET_ARN}:TG_BOT::"
            },
           {
                "name": "TG_CHAT_ID",
                "valueFrom": "${SECRET_ARN}:TG_CHAT_ID::"
            }
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "${LOG_GROUP_NAME}",
                "awslogs-region": "eu-west-2",
                "awslogs-stream-prefix": "ecs"
            }
        }
    }
]