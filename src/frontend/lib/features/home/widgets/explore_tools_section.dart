import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/theme/app_colors.dart';

/// 홈 화면 도구 모음 섹션.
///
/// 증상 검색, 부작용 검색, 질환별 주의약물 등 탐색 도구로의 진입점.
class ExploreToolsSection extends StatelessWidget {
  /// [ExploreToolsSection] 생성자.
  const ExploreToolsSection({super.key});

  static const _tools = [
    _ToolItem(
      icon: Icons.healing,
      label: '증상별\n약물 찾기',
      route: '/explore/symptoms',
      color: AppColors.info,
    ),
    _ToolItem(
      icon: Icons.warning_amber_rounded,
      label: '부작용\n역검색',
      route: '/explore/side-effects',
      color: AppColors.warning,
    ),
    _ToolItem(
      icon: Icons.local_hospital,
      label: '질환별\n주의약물',
      route: '/explore/conditions',
      color: AppColors.danger,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '도구 모음',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 12),
        Row(
          children: _tools.map((tool) {
            return Expanded(
              child: Padding(
                padding: EdgeInsets.only(
                  right: tool == _tools.last ? 0 : 8,
                ),
                child: _ToolCard(tool: tool),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class _ToolItem {
  final IconData icon;
  final String label;
  final String route;
  final Color color;

  const _ToolItem({
    required this.icon,
    required this.label,
    required this.route,
    required this.color,
  });
}

class _ToolCard extends StatelessWidget {
  final _ToolItem tool;

  const _ToolCard({required this.tool});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push(tool.route),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: tool.color.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(tool.icon, size: 24, color: tool.color),
              ),
              const SizedBox(height: 8),
              Text(
                tool.label,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12, height: 1.3),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
