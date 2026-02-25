import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:yakmeogeo/core/constants/app_constants.dart';
import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 설정 화면.
///
/// 이용약관, 개인정보 처리방침, 앱 정보, 오픈소스 라이선스 항목을 제공한다.
class SettingsScreen extends StatelessWidget {
  /// [SettingsScreen] 생성자.
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('설정'),
        centerTitle: false,
      ),
      body: ListView(
        children: [
          _buildLegalSection(context),
          const SizedBox(height: 16),
          _buildAppInfoSection(context),

          // 버전 정보
          const SizedBox(height: 32),
          const Center(
            child: Text(
              '${AppConstants.appName} v1.0.0',
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textDisabled,
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  /// 법적 정보 섹션을 구성한다.
  ///
  /// 이용약관, 개인정보 처리방침, 피드백 보내기 타일을 포함한다.
  Widget _buildLegalSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(title: '법적 정보'),
        _SettingsTile(
          icon: Icons.description_outlined,
          title: '이용약관',
          onTap: () => context.push('/settings/legal?type=terms'),
        ),
        const Divider(height: 1, indent: 56),
        _SettingsTile(
          icon: Icons.privacy_tip_outlined,
          title: '개인정보 처리방침',
          onTap: () => context.push('/settings/legal?type=privacy'),
        ),
        const Divider(height: 1, indent: 56),
        _SettingsTile(
          icon: Icons.feedback_outlined,
          title: '피드백 보내기',
          onTap: () => context.push('/settings/feedback'),
        ),
      ],
    );
  }

  /// 앱 정보 섹션을 구성한다.
  ///
  /// 앱 정보 다이얼로그 및 오픈소스 라이선스 타일을 포함한다.
  Widget _buildAppInfoSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(title: '앱 정보'),
        _SettingsTile(
          icon: Icons.info_outline,
          title: '앱 정보',
          onTap: () => _showAppInfoDialog(context),
        ),
        const Divider(height: 1, indent: 56),
        _SettingsTile(
          icon: Icons.code,
          title: '오픈소스 라이선스',
          onTap: () => showLicensePage(
            context: context,
            applicationName: AppConstants.appName,
            applicationVersion: '1.0.0',
          ),
        ),
      ],
    );
  }

  /// 앱 정보 다이얼로그를 표시한다.
  void _showAppInfoDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(AppConstants.appName),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppConstants.appTagline,
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
            SizedBox(height: 16),
            _InfoRow(label: '버전', value: '1.0.0'),
            SizedBox(height: 8),
            _InfoRow(label: '빌드', value: '1'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }
}

/// 설정 섹션 헤더.
class _SectionHeader extends StatelessWidget {
  /// [_SectionHeader] 생성자.
  const _SectionHeader({required this.title});

  /// 섹션 제목.
  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: AppColors.textSecondary,
        ),
      ),
    );
  }
}

/// 설정 항목 타일.
class _SettingsTile extends StatelessWidget {
  /// [_SettingsTile] 생성자.
  const _SettingsTile({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  /// 타일 아이콘.
  final IconData icon;

  /// 타일 제목.
  final String title;

  /// 탭 콜백.
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: AppColors.textSecondary, size: 22),
      title: Text(
        title,
        style: const TextStyle(fontSize: 15),
      ),
      trailing: const Icon(
        Icons.chevron_right,
        color: AppColors.textDisabled,
        size: 20,
      ),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
      minVerticalPadding: 14,
    );
  }
}

/// 앱 정보 다이얼로그 내 정보 행.
class _InfoRow extends StatelessWidget {
  /// [_InfoRow] 생성자.
  const _InfoRow({required this.label, required this.value});

  /// 라벨 텍스트.
  final String label;

  /// 값 텍스트.
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            color: AppColors.textSecondary,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            fontSize: 13,
            color: AppColors.textPrimary,
          ),
        ),
      ],
    );
  }
}
