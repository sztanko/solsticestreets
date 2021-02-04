provider "aws" {
  region = "eu-west-2"
}




resource "aws_vpc" "solsticestreets-vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "SolsticeStreets VPC"
  }

}

resource "aws_internet_gateway" "solsticestreets-gw" {
  vpc_id = aws_vpc.solsticestreets-vpc.id
  tags = {
    Name = "SolsticeStreets-vpc-gateway"
  }
}


resource "aws_route_table" "eu-west-2a-public" {
  vpc_id = aws_vpc.solsticestreets-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.solsticestreets-gw.id
  }

  tags = {
    Name        = "ss-2a-route"
    Environment = terraform.workspace
  }
}

resource "aws_route_table" "eu-west-2b-public" {
  vpc_id = aws_vpc.solsticestreets-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.solsticestreets-gw.id
  }

  tags = {
    Name = "ss-vpc-public-subnet-2b-route"
  }
}




resource "aws_subnet" "solsticestreets-subnet" {
  vpc_id            = aws_vpc.solsticestreets-vpc.id
  availability_zone = "eu-west-2a"
  cidr_block        = "10.0.1.0/24"

  tags = {
    Name = "SolsticeStreets-SUBNET"
  }
}

resource "aws_route_table_association" "eu-west-2a-public" {
  subnet_id      = aws_subnet.solsticestreets-subnet.id
  route_table_id = aws_route_table.eu-west-2a-public.id
}

resource "aws_security_group" "allow_all_a" {
  name        = "solsticestreets"
  description = "Allow all inbound traffic"
  vpc_id      = aws_vpc.solsticestreets-vpc.id


  ingress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"] # [aws_vpc.solsticestreets-vpc.cidr_block]
  }
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }
}


resource "aws_efs_file_system" "solsticestreets-scratch" {
  creation_token = "solsticestreets-scratch"

  tags = {
    Project = "solsticestreets"
    Name    = "SolsticeStreets Scratch"
  }
}

resource "aws_efs_mount_target" "solsticestreets-mount" {
  file_system_id  = aws_efs_file_system.solsticestreets-scratch.id
  subnet_id       = aws_subnet.solsticestreets-subnet.id
  security_groups = [aws_security_group.allow_all_a.id]

}

resource "aws_ecs_cluster" "solsticestreets-cluster" {
  name               = "solsticestreets-cluster"
  capacity_providers = ["FARGATE"]
}

resource "aws_ecs_task_definition" "solsticestreets-extractor" {
  family = "solsticestreets-extractor"

  container_definitions = file("container-defs/test.json")
  cpu                   = 4096
  memory                = 12288 // 12 GB

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  // task_role_arn = "arn:aws:iam::332309941764:role/ecsTaskExecutionRole"

  volume {
    name = "data"

    efs_volume_configuration {
      file_system_id = aws_efs_file_system.solsticestreets-scratch.id
      root_directory = "/"
      /*authorization_config {
        access_point_id = aws_efs_access_point.test.id
        iam             = "ENABLED"
      }*/
    }
  }


}
