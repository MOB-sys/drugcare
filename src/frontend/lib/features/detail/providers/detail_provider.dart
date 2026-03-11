import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/features/search/models/drug_detail.dart';
import 'package:pillright/features/search/models/food_detail.dart';
import 'package:pillright/features/search/models/herbal_medicine_detail.dart';
import 'package:pillright/features/search/models/supplement_detail.dart';

/// 약물 상세 정보 프로바이더.
final drugDetailProvider =
    FutureProvider.autoDispose.family<DrugDetail, int>((ref, drugId) async {
  final service = ref.read(drugServiceProvider);
  return service.getDrugDetail(drugId);
});

/// 영양제 상세 정보 프로바이더.
final supplementDetailProvider = FutureProvider.autoDispose
    .family<SupplementDetail, int>((ref, supplementId) async {
  final service = ref.read(supplementServiceProvider);
  return service.getSupplementDetail(supplementId);
});

/// 식품 상세 정보 프로바이더.
final foodDetailProvider =
    FutureProvider.autoDispose.family<FoodDetail, int>((ref, foodId) async {
  final service = ref.read(foodServiceProvider);
  return service.getFoodDetail(foodId);
});

/// 한약재 상세 정보 프로바이더.
final herbalMedicineDetailProvider = FutureProvider.autoDispose
    .family<HerbalMedicineDetail, int>((ref, herbalMedicineId) async {
  final service = ref.read(herbalMedicineServiceProvider);
  return service.getHerbalMedicineDetail(herbalMedicineId);
});
