pipeline {
  agent any

  environment {
    // These must match the credential IDs you already created in Jenkins
    GIT_CRED = 'github-pat'
    DOCKER_CRED = 'dockerhub-creds'
    SONAR_TOKEN_CRED = 'sonar-token'
    // Replace with your SonarQube URL before commit, or set as Jenkins global var
    SONAR_HOST_URL = 'http://http://localhost/:9000'
  }

  stages {
    stage('Checkout') {
      steps {
        // Multibranch will use the configured credential; plain checkout uses scm
        checkout scm
      }
    }

    stage('Build Docker image') {
      steps {
        script {
          // Use the username from docker credential to tag/push image
          withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh 'docker build -t ${DOCKER_USER}/7.3hdtask:${BUILD_NUMBER} .'
            sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
            sh 'docker push ${DOCKER_USER}/7.3hdtask:${BUILD_NUMBER}'
          }
        }
      }
    }

    stage('Unit Tests') {
      steps {
        sh '''
          python -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          mkdir -p results
          pytest -q --junitxml=results/junit.xml
        '''
        junit 'results/junit.xml'
      }
    }

    stage('Code Quality - SonarQube') {
      steps {
        withCredentials([string(credentialsId: env.SONAR_TOKEN_CRED, variable: 'SONAR_TOKEN')]) {
          // run sonar-scanner via docker image to avoid installing it on agent
          sh '''
            docker run --rm -v "$(pwd)":/usr/src -w /usr/src sonarsource/sonar-scanner-cli \
              -Dsonar.projectKey=7_3_hd_task \
              -Dsonar.sources=. \
              -Dsonar.host.url=${SONAR_HOST_URL} \
              -Dsonar.login=$SONAR_TOKEN \
              -Dsonar.exclusions=**/tests/**,**/.venv/**,**/__pycache__/**
          '''
        }
      }
    }

    stage('Security Scan (Trivy)') {
      steps {
        script {
          // Trivy via Docker (no token required for basic scans)
          withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            // ensure image exists locally; if not, docker pull might be required
            sh '''
              docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image \
                --severity CRITICAL,HIGH --no-progress ${DOCKER_USER}/7.3hdtask:${BUILD_NUMBER} || true
            '''
          }
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
      echo "Pipeline succeeded: image ${DOCKER_USER}/7.3hdtask:${BUILD_NUMBER}"
    }
    failure {
      echo "Pipeline failed - check console logs"
    }
  }
}
