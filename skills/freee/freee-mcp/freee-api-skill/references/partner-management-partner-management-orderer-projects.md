# partner_management_orderer_projects

partner_management_orderer_projects

## GET /hub/partner_management/orderer/projects/{id} — プロジェクト詳細取得（β版）

プロジェクト情報を取得する

### パラメータ

- freee-using-beta* (header): string - オープンベータのエンドポイントのため `true` を指定（必須） (選択肢: true)
- company_id*: integer(int64) - freee事業所ID
- id* (path): integer(int32) - 取得対象のプロジェクトID

### レスポンス

プロジェクト詳細レスポンス
- id*: integer(int32) - プロジェクトID
- is_archived*: boolean - アーカイブ済みかどうか
- archived_at*: string(date-time) - アーカイブ日時
- name*: string - プロジェクト名
- description*: string - 説明
- require_hide_other_freelancers*: boolean - 他パートナーのアカウントを非表示にするか
- default_inspection_date_days*: integer(int32) - 検収日のデフォルト設定
- default_task_order_note*: string - 発注書の備考欄のデフォルト設定
- default_invoice_note*: string - 請求書の備考欄のデフォルト設定
- approval_flow_pattern_task_order_id*: integer(int64) - タスク発注の社内承認フローID
- approval_flow_pattern_task_submit_id*: integer(int64) - タスク検収の社内承認フローID
- approval_flow_pattern_invoice_submit_id*: integer(int64) - 請求書の社内承認フローID
- created_at*: string(date-time) - 作成日時
