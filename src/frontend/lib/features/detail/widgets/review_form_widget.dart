import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/providers/review_provider.dart';
import 'package:pillright/features/detail/widgets/star_rating.dart';

/// 리뷰 작성 폼 위젯.
///
/// 별점 선택과 코멘트 입력을 제공한다.
class ReviewFormWidget extends ConsumerStatefulWidget {
  /// 아이템 유형.
  final String itemType;

  /// 아이템 ID.
  final int itemId;

  /// [ReviewFormWidget] 생성자.
  const ReviewFormWidget({
    super.key,
    required this.itemType,
    required this.itemId,
  });

  @override
  ConsumerState<ReviewFormWidget> createState() => _ReviewFormWidgetState();
}

class _ReviewFormWidgetState extends ConsumerState<ReviewFormWidget> {
  final _formKey = GlobalKey<FormState>();
  final _commentController = TextEditingController();

  int _rating = 0;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 별점 선택.
          Text(
            '별점을 선택해 주세요',
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          StarRating(
            rating: _rating,
            interactive: true,
            size: 32,
            onChanged: (value) => setState(() => _rating = value),
          ),
          const SizedBox(height: 16),
          // 코멘트 입력.
          TextFormField(
            controller: _commentController,
            maxLength: 500,
            maxLines: 3,
            decoration: InputDecoration(
              hintText: '리뷰를 남겨 주세요 (선택)',
              hintStyle: const TextStyle(color: AppColors.textDisabled),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              contentPadding: const EdgeInsets.all(12),
            ),
          ),
          const SizedBox(height: 12),
          // 제출 버튼.
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: _rating == 0 || _isSubmitting ? null : _submit,
              child: _isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('리뷰 등록'),
            ),
          ),
        ],
      ),
    );
  }

  /// 리뷰를 제출한다.
  Future<void> _submit() async {
    if (_rating == 0) return;

    setState(() => _isSubmitting = true);

    try {
      final key = ReviewKey(widget.itemType, widget.itemId);
      await ref.read(reviewListProvider(key).notifier).createReview(
            rating: _rating,
            comment: _commentController.text.trim(),
          );

      if (mounted) {
        setState(() {
          _rating = 0;
          _commentController.clear();
          _isSubmitting = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('리뷰가 등록되었습니다.')),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSubmitting = false);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('리뷰 등록에 실패했습니다: $e')),
        );
      }
    }
  }
}
