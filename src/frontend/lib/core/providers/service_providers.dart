import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/providers/dio_provider.dart';
import 'package:pillright/shared/services/cabinet_service.dart';
import 'package:pillright/shared/services/drug_service.dart';
import 'package:pillright/shared/services/interaction_service.dart';
import 'package:pillright/shared/services/reminder_service.dart';
import 'package:pillright/shared/services/feedback_service.dart';
import 'package:pillright/shared/services/supplement_service.dart';

/// 약물 검색/상세 API 서비스 프로바이더.
final drugServiceProvider = Provider<DrugService>((ref) {
  return DrugService(ref.read(dioProvider));
});

/// 영양제 검색/상세 API 서비스 프로바이더.
final supplementServiceProvider = Provider<SupplementService>((ref) {
  return SupplementService(ref.read(dioProvider));
});

/// 상호작용 체크 API 서비스 프로바이더.
final interactionServiceProvider = Provider<InteractionService>((ref) {
  return InteractionService(ref.read(dioProvider));
});

/// 복약함 API 서비스 프로바이더.
final cabinetServiceProvider = Provider<CabinetService>((ref) {
  return CabinetService(ref.read(dioProvider));
});

/// 리마인더 API 서비스 프로바이더.
final reminderServiceProvider = Provider<ReminderService>((ref) {
  return ReminderService(ref.read(dioProvider));
});

/// 피드백 API 서비스 프로바이더.
final feedbackServiceProvider = Provider<FeedbackService>((ref) {
  return FeedbackService(ref.read(dioProvider));
});
