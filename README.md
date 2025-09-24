# BPM GitOps Repository

GitOps конфигурации для BPM-system, основанные на Kustomize и индексируемые ArgoCD.

## Структура
```
clusters/
  base/                 # Общие манифесты сервисов (deployment/service)
  dev/                  # Оверлей dev-окружения (namespace bpm-dev)
  stage/                # Оверлей stage-окружения (namespace bpm-stage)
  prod/                 # Оверлей prod-окружения (namespace bpm-prod)
argo/
  applications/         # ApplicationSet для всех окружений
  projects/             # ArgoCD AppProject с правами доступа
```

Каждый оверлей включает сервисы:
- `bpm-gateway`
- `bpm-model-repo`
- `bpm-integration-workers`
- `bpm-etl`
- `bpm-ai-service`
- `bpm-ui-analyst`
- `bpm-ui-employee`
- `bpm-ui-clevel`

Базовые ресурсы лежат в `clusters/base/<service>` и переиспользуются dev/stage/prod Kustomize оверлеями, где задаются namespace и теги образов.

## ArgoCD
- `argo/projects/bpm.yaml` создаёт проект `bpm` с доступом ко всем окружениям.
- `argo/applications/bpm-platform.yaml` — ApplicationSet, который генерирует три приложения (`bpm-dev`, `bpm-stage`, `bpm-prod`) и синхронизирует директории `clusters/<env>`.
- Применение из корня репозитория:
  ```bash
  kubectl apply -n argocd -f argo/projects/bpm.yaml
  kubectl apply -n argocd -f argo/applications/bpm-platform.yaml
  ```

## Откат релиза
1. Определите нужный тег Docker-образа (например, из истории GitOps-коммитов или `docker images`).
2. Откройте соответствующий `clusters/<env>/<service>/kustomization.yaml` и замените `newTag` на требуемый тег.
3. Создайте коммит с сообщением `revert: <service> to <tag>` и отправьте его в `main` этого репозитория.
4. ArgoCD автоматически зафиксирует изменение; при необходимости выполните `argocd app sync bpm-<env>` для ускорения.
5. Убедитесь по `argocd app history bpm-<env>` или `kubectl rollout status` в целевом namespace, что откат завершён.

## Добавление нового сервиса
1. Создайте `clusters/base/<service>/` с базовыми манифестами (`deployment.yaml`, опционально `service.yaml`).
2. Добавьте оверлеи `clusters/dev|stage|prod/<service>/kustomization.yaml`, укажите namespace, список ресурсов `../../base/<service>` и `images` с `newTag`.
3. Пропишите директорию сервиса в `clusters/<env>/kustomization.yaml` для всех окружений.
4. Обновите CI-пайплайн нового сервиса: в шаге обновления GitOps укажите путь `gitops/clusters/dev/<service>/kustomization.yaml`.
5. Примените ArgoCD ApplicationSet (см. выше), чтобы Argo увидел новый сервис.

## Секреты CI/CD
- `YC_TOKEN` — OAuth-токен сервисного аккаунта с ролью `container-registry.images.pusher`. Хранится в [Yandex Lockbox](https://cloud.yandex.ru/services/lockbox) в записи `bpm-ci-registry`; в GitHub репозиториях сервисов публикуется через секрет `YC_TOKEN`.
- `GITOPS_TOKEN` — персональный токен технического пользователя GitHub с доступом `repo` только к `bpm-gitops`. Хранится в Lockbox записи `bpm-ci-gitops`, синхронизируется в секрет `GITOPS_TOKEN` Action'ов.
- `REGISTRY_USERNAME`/`REGISTRY_PASSWORD` — статичный логин/пароль контейнерного реестра (альтернатива `YC_TOKEN` для локальных запусков). Создаются через YC CLI, лежат в Lockbox `bpm-ci-registry-basic`.
- Deploy key `bpm-gitops-deploy` — read/write ключ для GitHub Actions, добавлен в настройках `bpm-gitops` как Deploy Key и в секретном хранилище Lockbox `bpm-ci-gitops-key`.

Ротация секретов:
1. Выпустить новый токен или ключ (YC CLI или GitHub UI).
2. Обновить запись в Lockbox; в CI пайплайнах секрет подтягивается командой `yc lockbox secret get-value`, которая выполняется перед запуском GitHub Actions runners.
3. Обновить секреты GitHub (`Settings → Secrets and variables → Actions`). Для deploy key — добавить новый ключ и переключить Actions на него, затем удалить старый.
4. Перезапустить пайплайн сервиса (`Actions → Run workflow`) и убедиться, что шаги логина в реестр и push в GitOps проходят успешно.

## Требования
- ArgoCD установлен в кластере (см. `repos/bpm-infra/scripts/install-argocd.sh`).
- GitHub Actions сервисов публикуют образы в `cr.yandex/bpm-registry/<service>` и обновляют тег `newTag`.
- Доступ к Yandex Container Registry и Kubernetes кластеру настроен для CI/CD и операторов.
