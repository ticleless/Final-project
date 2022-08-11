# devops-02-Final-TeamD-scenario1
## 요구사항
- AWS 계정이 필요합니다. IAM 사용자일 경우 서비스를 호출하고 관리할 수 있는 권한이 필요합니다.
- AWS CLI 설치 및 configure 구성
- Git 설치
- TerraForm 설치
## 배포 방법
1. 새 디렉토리를 만들고 해당 디렉토리로 이동한다음 GitHub repository를 Clone합니다.
    ```
    git clone https://github.com/cs-devops-bootcamp/devops-02-Final-TeamD-scenario1.git
    ```
2. 디렉토리를 terraform 디렉토리로 변경합니다.
    ```
    cd terraform
    ```
3. 명령줄에서 terraform init을 입력하여 tf 파일에 구성된 provider에 맞는 플러그인을 다운로드합니다.
    ```
    terraform init
    ```

4. 명령줄에서 terraform을 사용하여 tf 파일에 구성된 대로 AWS 리소스를 배포합니다.
배포 완료까지는 약 15분 소요 될 수 있습니다.
    ```
    terraform deploy
    ```
5. Deploy가 완료되면 AWS Management Console에서 Amazon OpenSearch Service로 접속합니다.

6. 배포된 도메인에 해당하는 OpenSearch Dash board URL로 접속합니다.

7. user가 OpenSearch 클러스터와 인덱스에 접근할 수 있도록 하는 권한을 부여하기 위해 먼저 Role을 생성합니다.
![role](https://user-images.githubusercontent.com/78151046/184048274-9f26076b-eedb-4afe-8376-2c7e23b0b6da.jpg)

    - Create Role 
    
    - Name(자유롭게) 작성
    
    - Cluster permissions - `cluster_all`, `indices_all` 부여 
    
    - Index permissions - index에는 `*` 삽입, Index permissions는 Cluster            permissons와 동일하게 권한 부여
    - 나머지 항목은 무시합니다.
8. Role이 생성되면 생성된 Role을 user에 매핑해줘야 함니다.
![mapping](https://user-images.githubusercontent.com/78151046/184048300-30622a82-343b-481c-b2f7-8bcd390bea64.jpg)

    - 생성된 Role name 클릭 ->Mapped users 클릭 -> Manage mapping 클릭
    - Users에 자신이 사용하는 AWS user(사용자) ARN을 삽입합니다. 추가적으로  다른 IAM 사용자도 DashBoard를 구성한다면 그 사용자의 ARN도 삽입합니다.
    - Backend roles는 AWS IAM에서 새로운 역할을 `AmazonOpenSearchFullAccess` 정책을 추가하여 만들고 새로 구성된 Role ARN을 Backend roles에 삽입합니다.

## 인덱스 생성 및 매핑
OpenSearch Dashboard - Dev tool로 이동하여 아래의 코드를 붙여넣고 실행합니다. `geo_point` data type이 자동으로 매핑되지 않기 때문에 인덱스에 매핑 되기 전 직접 전체 매핑을 해줘야 합니다. `weather`는 변경 가능한 인덱스 명입니다.
```
PUT /weather
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  },
  
  "mappings": {
      "properties" : {
        "co2" : {
          "type" : "long"
        },
        "coord" : {
          "type": "geo_point"
        },
        "device_id" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "error_code" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "humidity" : {
          "type" : "long"
        },
        "pressure" : {
          "type" : "long"
        },
        "result" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "server_time" : {
          "type" : "date"
        },
        "temperature" : {
          "type" : "long"
        }
      }
    }
}
```
해당 코드를 입력하였다면 OpenSearch Dashboards - Management - Stack Management - Index patterns에 들어갑니다.

Create index pattern을 클릭하고 위의 코드에서 넣었던 인덱스 명을 선택해 인덱스 패턴을 생성합니다.

올바르게 데이터 타입이 들어갔는지 확인합니다.
