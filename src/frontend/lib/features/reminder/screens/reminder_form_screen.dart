import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/core/utils/date_utils.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/features/reminder/models/reminder.dart';
import 'package:pillright/features/reminder/providers/reminder_provider.dart';
import 'package:pillright/shared/widgets/common/error_widget.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';

/// 복약함 아이템 목록 프로바이더 (폼에서 드롭다운용).
final _cabinetItemsProvider =
    FutureProvider.autoDispose<List<CabinetItem>>((ref) async {
  final service = ref.read(cabinetServiceProvider);
  return service.listItems();
});

/// 리마인더 생성/수정 폼 화면.
///
/// GoRouter extra로 [Reminder]를 전달하면 수정 모드,
/// null이면 생성 모드로 동작한다.
class ReminderFormScreen extends ConsumerStatefulWidget {
  /// [ReminderFormScreen] 생성자.
  ///
  /// [existingReminder] — 수정할 리마인더 (null이면 생성 모드).
  const ReminderFormScreen({super.key, this.existingReminder});

  /// 수정할 기존 리마인더.
  final Reminder? existingReminder;

  @override
  ConsumerState<ReminderFormScreen> createState() =>
      _ReminderFormScreenState();
}

/// [ReminderFormScreen]의 상태 관리 클래스.
class _ReminderFormScreenState extends ConsumerState<ReminderFormScreen> {
  /// 폼 글로벌 키.
  final _formKey = GlobalKey<FormState>();

  /// 선택된 복약함 아이템 ID.
  int? _selectedCabinetItemId;

  /// 선택된 알림 시간.
  TimeOfDay _selectedTime = const TimeOfDay(hour: 9, minute: 0);

  /// 선택된 반복 요일 목록.
  final List<int> _selectedDays = [];

  /// 메모 텍스트 컨트롤러.
  final _memoController = TextEditingController();

  /// 저장 진행 중 여부.
  bool _isSaving = false;

  /// 수정 모드 여부.
  bool get _isEditing => widget.existingReminder != null;

  @override
  void initState() {
    super.initState();
    final existing = widget.existingReminder;
    if (existing != null) {
      _selectedCabinetItemId = existing.cabinetItemId;
      final parsed = AppDateUtils.parseTime(existing.reminderTime);
      _selectedTime = TimeOfDay(hour: parsed.hour, minute: parsed.minute);
      _selectedDays.addAll(existing.daysOfWeek);
      _memoController.text = existing.memo ?? '';
    }
  }

  @override
  void dispose() {
    _memoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cabinetAsync = ref.watch(_cabinetItemsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? '리마인더 수정' : '리마인더 추가'),
      ),
      body: cabinetAsync.when(
        loading: () => const LoadingWidget(message: '복약함 목록 불러오는 중...'),
        error: (err, _) => AppErrorWidget(
          message: err.toString(),
          onRetry: () => ref.invalidate(_cabinetItemsProvider),
        ),
        data: (cabinetItems) => _buildForm(cabinetItems),
      ),
    );
  }

  /// 폼 본문을 빌드한다.
  Widget _buildForm(List<CabinetItem> cabinetItems) {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildItemDropdown(cabinetItems),
          const SizedBox(height: 20),
          _buildTimePicker(),
          const SizedBox(height: 20),
          _buildDaySelector(),
          const SizedBox(height: 20),
          _buildMemoField(),
          const SizedBox(height: 32),
          _buildSaveButton(),
        ],
      ),
    );
  }

  /// 복약 아이템 드롭다운을 빌드한다.
  Widget _buildItemDropdown(List<CabinetItem> cabinetItems) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '복약 아이템',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<int>(
          initialValue: _selectedCabinetItemId,
          decoration: const InputDecoration(
            hintText: '복약함에서 아이템을 선택하세요',
          ),
          items: cabinetItems.map((item) {
            return DropdownMenuItem<int>(
              value: item.id,
              child: Text(
                item.nickname ?? item.itemName,
                overflow: TextOverflow.ellipsis,
              ),
            );
          }).toList(),
          onChanged: _isEditing
              ? null
              : (value) => setState(() => _selectedCabinetItemId = value),
          validator: (value) {
            if (value == null) return '아이템을 선택해 주세요';
            return null;
          },
        ),
      ],
    );
  }

  /// 시간 선택기를 빌드한다.
  Widget _buildTimePicker() {
    final timeStr = AppDateUtils.formatTime(
      _selectedTime.hour,
      _selectedTime.minute,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '알림 시간',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 8),
        InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: _pickTime,
          child: _buildTimeDisplay(timeStr),
        ),
      ],
    );
  }

  /// 시간 아이콘과 텍스트를 포함하는 디스플레이 컨테이너를 빌드한다.
  ///
  /// [timeStr] — "HH:mm" 형식의 시간 문자열.
  Widget _buildTimeDisplay(String timeStr) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 14,
      ),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.divider),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.access_time,
            color: AppColors.primary,
            size: 20,
          ),
          const SizedBox(width: 12),
          Text(
            timeStr,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  /// 시간 선택 다이얼로그를 표시한다.
  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime,
    );
    if (picked != null) {
      setState(() => _selectedTime = picked);
    }
  }

  /// 요일 선택기를 빌드한다.
  Widget _buildDaySelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '반복 요일',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: List.generate(7, _buildDayChip),
        ),
        if (_selectedDays.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 6),
            child: Text(
              '최소 1개 요일을 선택해 주세요',
              style: TextStyle(
                fontSize: 12,
                color: AppColors.danger,
              ),
            ),
          ),
      ],
    );
  }

  /// 개별 요일 선택 칩을 빌드한다.
  ///
  /// [index] — 요일 인덱스 (0=월 ~ 6=일, 백엔드 규격 일치).
  Widget _buildDayChip(int index) {
    final day = index;
    final isSelected = _selectedDays.contains(day);
    final label = AppDateUtils.weekdayName(index);

    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      selectedColor: AppColors.primaryLight,
      labelStyle: TextStyle(
        color: isSelected
            ? AppColors.primaryDark
            : AppColors.textSecondary,
        fontWeight:
            isSelected ? FontWeight.w600 : FontWeight.normal,
      ),
      onSelected: (selected) {
        setState(() {
          if (selected) {
            _selectedDays.add(day);
          } else {
            _selectedDays.remove(day);
          }
        });
      },
    );
  }

  /// 메모 입력 필드를 빌드한다.
  Widget _buildMemoField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '메모 (선택)',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _memoController,
          decoration: const InputDecoration(
            hintText: '예: 식후 30분',
          ),
          maxLines: 2,
          maxLength: 100,
        ),
      ],
    );
  }

  /// 저장 버튼을 빌드한다.
  Widget _buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton(
        onPressed: _isSaving ? null : _onSave,
        child: _isSaving
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : Text(_isEditing ? '수정 완료' : '리마인더 추가'),
      ),
    );
  }

  /// 저장에 필요한 폼 데이터를 준비하여 레코드로 반환한다.
  ///
  /// 반환값은 `timeWithSeconds` (HH:mm:ss 형식), `days` (선택된 요일 복사본),
  /// `memo` (빈 문자열이면 null) 세 필드를 갖는 레코드이다.
  ({String timeWithSeconds, List<int> days, String? memo}) _buildSavePayload() {
    final timeStr = AppDateUtils.formatTime(
      _selectedTime.hour,
      _selectedTime.minute,
    );
    final timeWithSeconds = '$timeStr:00';
    final memo =
        _memoController.text.trim().isEmpty ? null : _memoController.text.trim();

    return (
      timeWithSeconds: timeWithSeconds,
      days: List<int>.from(_selectedDays),
      memo: memo,
    );
  }

  /// 폼을 검증하고 저장한다.
  Future<void> _onSave() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedDays.isEmpty) return;

    setState(() => _isSaving = true);

    try {
      final payload = _buildSavePayload();
      final notifier = ref.read(reminderProvider.notifier);

      if (_isEditing) {
        await notifier.updateReminder(
          widget.existingReminder!.id,
          ReminderUpdate(
            reminderTime: payload.timeWithSeconds,
            daysOfWeek: payload.days,
            memo: payload.memo,
          ),
        );
      } else {
        await notifier.createReminder(
          ReminderCreate(
            cabinetItemId: _selectedCabinetItemId!,
            reminderTime: payload.timeWithSeconds,
            daysOfWeek: payload.days,
            memo: payload.memo,
          ),
        );
      }

      if (mounted) context.pop();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('저장 실패: $e'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }
}
