# Shadowverse: Worlds Beyond AI

Shadowverse: Worlds Beyond の AI エージェント。中ランクのヒューマンプレイヤーに対して 55% 以上の勝率を目指す自己対戦学習プロジェクト。

## プロジェクト構成

```
svwb_ai/
├── engine/          # ゲームエンジン
│   ├── game_state.py
│   ├── game_manager.py
│   ├── legal_actions.py
│   ├── effect_engine.py
│   ├── action.py
│   ├── mulligan.py
│   └── cards/
├── ai/              # AI エージェント
│   ├── base_agent.py
│   ├── random_agent.py
│   └── rule_agent.py
├── config/          # ゲーム設定
│   └── game_config.py
├── tests/           # ユニットテスト
└── training/        # 学習関連（Phase 2-4）
```

## Phase 進行状況

- [x] **Phase 1**: ゲームエンジン実装
  - ゲーム状態管理
  - リーガルアクション生成
  - エフェクトエンジン
  - ルール型 AI
  - 8/8 テスト合格

- [ ] **Phase 2**: ルール型 AI 強化と検証
- [ ] **Phase 3**: MCTS 実装
- [ ] **Phase 4**: 強化学習ループ（100万ゲーム自己対戦）

## 使用方法

### テスト実行

```bash
python -m pytest svwb_ai/tests/ -v
```

### デモゲーム

```bash
python svwb_ai/demo_game.py
```

## 学習環境

- **開発**: ローカル環境
- **学習**: Google Colab (T4/V100 GPU)
- **保存**: Google Drive

## 技術スタック

- Python 3.10+
- PyTorch (Phase 4)
- AlphaZero-style 自己対戦学習
- MCTS (Monte Carlo Tree Search)

## ライセンス

Private project
