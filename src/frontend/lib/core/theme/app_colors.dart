import 'package:flutter/material.dart';

/// 앱 색상 팔레트 — 신호등 시스템 + 브랜딩.
class AppColors {
  /// 인스턴스 생성 방지용 private 생성자.
  AppColors._();

  // ── 브랜드 색상 ──
  /// 프라이머리 (민트/청록).
  static const Color primary = Color(0xFF00BFA5);

  /// 프라이머리 라이트.
  static const Color primaryLight = Color(0xFFB2DFDB);

  /// 프라이머리 다크.
  static const Color primaryDark = Color(0xFF00897B);

  // ── 신호등 색상 (상호작용 심각도) ──
  /// 위험 (danger) — 빨간색.
  static const Color danger = Color(0xFFD32F2F);

  /// 위험 배경.
  static const Color dangerBg = Color(0xFFFFEBEE);

  /// 경고 (warning) — 주황색.
  static const Color warning = Color(0xFFF57C00);

  /// 경고 배경.
  static const Color warningBg = Color(0xFFFFF3E0);

  /// 주의 (caution) — 노란색.
  static const Color caution = Color(0xFFFBC02D);

  /// 주의 배경.
  static const Color cautionBg = Color(0xFFFFFDE7);

  /// 안전/정보 (info) — 파란색.
  static const Color info = Color(0xFF1976D2);

  /// 안전/정보 배경.
  static const Color infoBg = Color(0xFFE3F2FD);

  /// 안전 (safe) — 녹색.
  static const Color safe = Color(0xFF388E3C);

  /// 안전 배경.
  static const Color safeBg = Color(0xFFE8F5E9);

  // ── 중립 색상 ──
  /// 배경색.
  static const Color background = Color(0xFFF5F5F5);

  /// 표면색.
  static const Color surface = Color(0xFFFFFFFF);

  /// 텍스트 기본.
  static const Color textPrimary = Color(0xFF212121);

  /// 텍스트 보조.
  static const Color textSecondary = Color(0xFF757575);

  /// 텍스트 비활성.
  static const Color textDisabled = Color(0xFFBDBDBD);

  /// 구분선.
  static const Color divider = Color(0xFFE0E0E0);

  /// 약물 태그 색상.
  static const Color drugTag = Color(0xFF42A5F5);

  /// 영양제 태그 색상.
  static const Color supplementTag = Color(0xFF66BB6A);
}
