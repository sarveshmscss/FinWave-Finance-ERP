provider "aws" {
  region = "ap-south-1" # Asia Pacific (Mumbai) region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = "main_vpc"
  }
}

resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-south-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "main_subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main_igw"
  }
}

resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "main_route_table"
  }
}

resource "aws_route_table_association" "main" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

resource "aws_security_group" "instance" {
  vpc_id = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Adjust this to restrict access to specific IP addresses for security
  }

  tags = {
    Name = "instance_sg"
  }
}

resource "aws_instance" "web" {
  ami                    = "ami-0ad21ae1d0696ad58" # Ubuntu 22.04 LTS AMI ID for Asia Pacific (Mumbai)
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.instance.id]
  key_name               = "key" # Replace with your key pair name

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y python3 python3-pip mysql-client
              pip3 install flask mysql-connector-python gunicorn

              # Setup MySQL client configuration
              echo "[client]" > /etc/mysql/my.cnf
              echo "user=root" >> /etc/mysql/my.cnf
              echo "password=Sarvesh@123" >> /etc/mysql/my.cnf

              # Navigate to project directory and run the Flask application
              cd /home/ubuntu/FinWave-ERP
              gunicorn -w 4 -b 0.0.0.0:5000 finwave:app
              EOF

  tags = {
    Name = "web_instance"
  }
}
