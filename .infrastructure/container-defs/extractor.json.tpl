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
            }
        ]
    }
]