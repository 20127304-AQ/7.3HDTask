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

        stage('Build stage') {
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

        stage('Test stage') {
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
                        docker run --rm -v "%CD%:/usr/src" -w /usr/src sonarsource/sonar-scanner-cli ^
                          -Dsonar.login=%SONAR_TOKEN%
                    """
                }
            }
        }

        stage('Security') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
        REM Set absolute workspace path
        set WORKDIR=%CD%

        REM Scan Docker image with Trivy and export JSON to host directory
        docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v "%WORKDIR%:/scan" aquasec/trivy image ^
          --severity CRITICAL,HIGH --format json --output /scan/trivy_report.json %DOCKER_USER%/7.3hdtask:%BUILD_NUMBER%

        REM Debug: check if file exists
        dir trivy_report.json

        REM Parse JSON to list vulnerabilities using Python (Windows-compatible)
        echo import json > parse_trivy.py
        echo with open("trivy_report.json") as f: >> parse_trivy.py
        echo     report = json.load(f) >> parse_trivy.py
        echo if 'Results' in report: >> parse_trivy.py
        echo     for result in report['Results']: >> parse_trivy.py
        echo         if 'Vulnerabilities' in result: >> parse_trivy.py
        echo             for vuln in result['Vulnerabilities']: >> parse_trivy.py
        echo                 name = vuln.get('VulnerabilityID', 'N/A') >> parse_trivy.py
        echo                 severity = vuln.get('Severity', 'N/A') >> parse_trivy.py
        echo                 fix = vuln.get('FixedVersion', 'Not available') >> parse_trivy.py
        echo                 print(f"Issue: {name}, Severity: {severity}, Fixed Version: {fix}") >> parse_trivy.py

        python parse_trivy.py
        del parse_trivy.py
        """
                    archiveArtifacts artifacts: 'trivy_report.json', allowEmptyArchive: true
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
