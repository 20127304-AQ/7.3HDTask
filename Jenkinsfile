pipeline {
    agent any

    environment {
        DOCKER_CRED = 'dockerhub-creds'
        SONAR_TOKEN_CRED = 'sonar-token'
        SONAR_HOST_URL = 'http://host.docker.internal:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "docker build -t %DOCKER_USER%/7.3hdtask:%BUILD_NUMBER% ."
                        bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                        bat "docker push %DOCKER_USER%/7.3hdtask:%BUILD_NUMBER%"
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    mkdir results
                    pytest --junitxml=results\\junit.xml
                '''
                junit 'results/junit.xml'
            }
        }

        stage('Code Quality - SonarQube') {
            steps {
                withCredentials([string(credentialsId: env.SONAR_TOKEN_CRED, variable: 'SONAR_TOKEN')]) {
                    bat """
                        docker run --rm -v "%CD%:/usr/src" -w /usr/src -e SONAR_TOKEN=%SONAR_TOKEN% sonarsource/sonar-scanner-cli ^
                          -Dsonar.projectKey=7_3_hd_task ^
                          -Dsonar.sources=. ^
                          -Dsonar.host.url=%SONAR_HOST_URL% ^
                          -Dsonar.login=%SONAR_TOKEN% ^
                          -Dsonar.exclusions=**/tests/**,**/venv/**,**/__pycache__/**
                    """
                }
            }
        }


        stage('Security Scan (Trivy)') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                        docker run --rm -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ^
                          --severity CRITICAL,HIGH --no-progress %DOCKER_USER%/7.3hdtask:%BUILD_NUMBER% || exit 0
                    """
                }
            }
        }

        stage('Archive artifacts') {
            steps {
                archiveArtifacts artifacts: 'results/**', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded: image pushed and tests passed."
        }
        failure {
            echo "Pipeline failed - check console logs"
        }
    }
}
