pipeline{
	agent any
	stages{
		stage("代码拉取"){
			steps{
				checkout scm
			}
		}
		stage("安装依赖"){
			steps{
				bat 'python -m pip install -q requests pytest allure-pytest'
			}
		}
		stage("运行测试"){
			steps{
				bat '''
				start /b python login_mock.py 8000
				set /a tries=0
				:waitloop
				curl --fail -s -o nul http://127.0.0.1:8000/login
				if %ERRORLEVEL%==0 goto ready
				set /a tries+=1
				echo probe failed, attempt %tries%
				if %tries% geq 10 exit /b 1
				ping -n 2 127.0.0.1 > nul
				goto waitloop
				:ready
				echo service ready, failed probes: %tries%
				python -m pytest -v
				set RESULT=%ERRORLEVEL%
				for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a > nul 2>&1
				exit /b %RESULT%
				'''
			}
		}
	}
	post{
		success{
			bat 'echo 运行成功'
		}
		failure{
			bat 'echo 运行失败'
		}
		always{
			bat 'echo 运行结束'
		}
	}
}