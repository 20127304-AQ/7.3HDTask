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
                        REM Scan image with Trivy and export JSON
                        docker run --rm -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ^
                          --severity CRITICAL,HIGH --format json --output trivy_report.json %DOCKER_USER%/7.3hdtask:%BUILD_NUMBER%
                    """

                    bat """
                        REM Parse JSON to list vulnerabilities (name, severity, fix)
                        python - <<END
        import json

        with open("trivy_report.json") as f:
            report = json.load(f)

        if 'Results' in report:
            for result in report['Results']:
                if 'Vulnerabilities' in result:
                    for vuln in result['Vulnerabilities']:
                        name = vuln.get('VulnerabilityID', 'N/A')
                        severity = vuln.get('Severity', 'N/A')
                        fix = vuln.get('FixedVersion', 'Not available')
                        print(f"Issue: {name}, Severity: {severity}, Fixed Version: {fix}")
        END
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
