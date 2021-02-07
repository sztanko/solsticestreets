[
    {
        "name": "solsticestreets-prod",
        "image": "ubuntu",
        "essential": true,
        "command": [
            "/bin/bash",
            "-c",
            "echo $GIT_TOKEN >> /data/date.txt"
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
            }
        ]
    }
]