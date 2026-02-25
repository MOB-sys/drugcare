import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/core/providers/service_providers.dart';
import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 피드백 카테고리 옵션.
const _categories = [
  ('bug', '버그 신고'),
  ('feature', '기능 제안'),
  ('data_error', '데이터 오류'),
  ('other', '기타'),
];

/// 피드백 제출 화면.
///
/// 베타 사용자가 버그 신고, 기능 제안, 데이터 오류 등을 제출할 수 있다.
class FeedbackScreen extends ConsumerStatefulWidget {
  /// [FeedbackScreen] 생성자.
  const FeedbackScreen({super.key});

  @override
  ConsumerState<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends ConsumerState<FeedbackScreen> {
  final _formKey = GlobalKey<FormState>();
  final _contentController = TextEditingController();
  String _selectedCategory = 'bug';
  bool _isSubmitting = false;

  @override
  void dispose() {
    _contentController.dispose();
    super.dispose();
  }

  /// 피드백을 제출한다.
  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final feedbackService = ref.read(feedbackServiceProvider);
      await feedbackService.submit(
        category: _selectedCategory,
        content: _contentController.text.trim(),
        osInfo: '${Platform.operatingSystem} ${Platform.operatingSystemVersion}',
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('피드백이 제출되었습니다. 감사합니다!'),
            backgroundColor: AppColors.safe,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('피드백 제출에 실패했습니다. 잠시 후 다시 시도해주세요.'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  /// 피드백 카테고리 선택 섹션을 빌드한다.
  ///
  /// 카테고리 라벨과 [ChoiceChip] 목록을 [Wrap]으로 배치한다.
  Widget _buildCategorySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '카테고리',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: _categories.map((cat) {
            final isSelected = _selectedCategory == cat.$1;
            return ChoiceChip(
              label: Text(cat.$2),
              selected: isSelected,
              onSelected: (_) {
                setState(() => _selectedCategory = cat.$1);
              },
              selectedColor: AppColors.primary.withValues(alpha: 0.15),
              labelStyle: TextStyle(
                color: isSelected
                    ? AppColors.primary
                    : AppColors.textSecondary,
                fontWeight:
                    isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  /// 피드백 내용 입력 필드를 빌드한다.
  ///
  /// '내용' 라벨과 최대 2000자의 [TextFormField]를 반환한다.
  Widget _buildContentField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '내용',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _contentController,
          maxLines: 6,
          maxLength: 2000,
          decoration: InputDecoration(
            hintText: '피드백 내용을 입력해주세요...',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.all(16),
          ),
          validator: (value) {
            if (value == null || value.trim().length < 5) {
              return '5자 이상 입력해주세요.';
            }
            return null;
          },
        ),
      ],
    );
  }

  /// 피드백 제출 버튼을 빌드한다.
  ///
  /// 제출 중일 때는 [CircularProgressIndicator]를 표시하고,
  /// 그렇지 않으면 '피드백 보내기' 텍스트를 표시한다.
  Widget _buildSubmitButton() {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(
        onPressed: _isSubmitting ? null : _submit,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isSubmitting
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : const Text(
                '피드백 보내기',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('피드백 보내기'),
        centerTitle: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '서비스 개선에 도움이 되는 소중한 의견을 보내주세요.',
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 24),
              _buildCategorySection(),
              const SizedBox(height: 24),
              _buildContentField(),
              const SizedBox(height: 32),
              _buildSubmitButton(),
            ],
          ),
        ),
      ),
    );
  }
}
