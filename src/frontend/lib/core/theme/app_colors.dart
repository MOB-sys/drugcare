import 'package:flutter/material.dart';

/// 앱 색상 팔레트 — 웹과 통일된 Deep Navy + Teal 시스템.
class AppColors {
  /// 인스턴스 생성 방지용 private 생성자.
  AppColors._();

  // ── 브랜드 색상 (Deep Navy) ──
  /// 프라이머리 (딥 네이비).
  static const Color primary = Color(0xFF1B3A5C);

  /// 프라이머리 라이트.
  static const Color primaryLight = Color(0xFFEEF2F7);

  /// 프라이머리 100.
  static const Color primary100 = Color(0xFFD4DDE9);

  /// 프라이머리 다크.
  static const Color primaryDark = Color(0xFF132B45);

  // ── 액센트 (Teal) ──
  /// 액센트 (틸).
  static const Color accent = Color(0xFF0D9488);

  // ── 신호등 색상 (상호작용 심각도) ──
  /// 위험 (danger) — 빨간색.
  static const Color danger = Color(0xFFDC2626);

  /// 위험 배경.
  static const Color dangerBg = Color(0xFFFEF2F2);

  /// 경고 (warning) — 주황색.
  static const Color warning = Color(0xFFEA580C);

  /// 경고 배경.
  static const Color warningBg = Color(0xFFFFF7ED);

  /// 주의 (caution) — 노란색.
  static const Color caution = Color(0xFFCA8A04);

  /// 주의 배경.
  static const Color cautionBg = Color(0xFFFEFCE8);

  /// 안전/정보 (info) — 파란색.
  static const Color info = Color(0xFF2563EB);

  /// 안전/정보 배경.
  static const Color infoBg = Color(0xFFEFF6FF);

  /// 안전 (safe) — 녹색.
  static const Color safe = Color(0xFF16A34A);

  /// 안전 배경.
  static const Color safeBg = Color(0xFFF0FDF4);

  // ── 중립 색상 (라이트 모드) ──
  /// 배경색.
  static const Color background = Color(0xFFF8FAFC);

  /// 표면색.
  static const Color surface = Color(0xFFFFFFFF);

  /// 표면 호버.
  static const Color surfaceHover = Color(0xFFF9FAFB);

  /// 텍스트 기본.
  static const Color textPrimary = Color(0xFF111827);

  /// 텍스트 보조.
  static const Color textSecondary = Color(0xFF6B7280);

  /// 텍스트 비활성.
  static const Color textDisabled = Color(0xFF9CA3AF);

  /// 구분선.
  static const Color divider = Color(0xFFE5E7EB);

  /// 구분선 라이트.
  static const Color dividerLight = Color(0xFFF3F4F6);

  // ── 다크 모드 색상 ──
  /// 다크 배경색.
  static const Color darkBackground = Color(0xFF0F172A);

  /// 다크 표면색.
  static const Color darkSurface = Color(0xFF1E293B);

  /// 다크 표면 호버.
  static const Color darkSurfaceHover = Color(0xFF334155);

  /// 다크 프라이머리.
  static const Color darkPrimary = Color(0xFF7EB0D5);

  /// 다크 액센트.
  static const Color darkAccent = Color(0xFF2DD4BF);

  /// 다크 텍스트 기본.
  static const Color darkTextPrimary = Color(0xFFF1F5F9);

  /// 다크 텍스트 보조.
  static const Color darkTextSecondary = Color(0xFF94A3B8);

  /// 다크 텍스트 비활성.
  static const Color darkTextDisabled = Color(0xFF64748B);

  /// 다크 구분선.
  static const Color darkDivider = Color(0xFF334155);

  /// 약물 태그 색상.
  static const Color drugTag = Color(0xFF3B82F6);

  /// 영양제 태그 색상.
  static const Color supplementTag = Color(0xFF10B981);
}
