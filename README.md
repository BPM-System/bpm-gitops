# BPM GitOps Repository

Этот репозиторий содержит Kustomize/ArgoCD манифесты для BPM-system.

## Структура
```
clusters/
  dev/
    bpm-gateway/
    bpm-model-repo/
    bpm-integration-workers/
    kustomization.yaml
    namespace.yaml
argo/
  applications/
  projects/
```

## Манифесты
- Для каждого сервиса определён собственный `kustomization` с образом в `cr.yandex/bpm-registry/<service>`.
- Тег образа (`newTag`) обновляется CI пайплайном после успешного пуша.

## ArgoCD
- Приложения описаны в `argo/applications`. Пример применения:
  ```bash
  kubectl apply -n argocd -f argo/applications/dev-bpm.yaml
  ```
- Для prod/stage можно создать аналогичные директории `clusters/stage`, `clusters/prod`.

## Namespace
- `namespace.yaml` создаёт namespace `bpm-dev`.

## Требования
- Установленный ArgoCD (helm chart или manifests) в кластере.
- Доступ к Yandex Container Registry `bpm-registry`.
- CI должен обновлять тег образа и коммитить в этот репозиторий.
