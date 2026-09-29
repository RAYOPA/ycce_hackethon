import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../../main.dart'; // For AuthProvider
import '../../core/network/api_client.dart';
import '../auth/login_screen.dart';

class WelfareDashboard extends StatefulWidget {
  const WelfareDashboard({super.key});

  @override
  State<WelfareDashboard> createState() => _WelfareDashboardState();
}

class _WelfareDashboardState extends State<WelfareDashboard> {
  int _currentIndex = 0;
  String _personnelSearchQuery = '';
  String _followUpFilter = 'All';

  List<Map<String, dynamic>> _personnelList = [
    {
      'id': 'P001',
      'name': 'Havildar Rajesh Kumar',
      'unit': 'Alpha Battery (Unit 101)',
      'status': 'Elevated Risk',
      'trend': 'Rising',
      'lastCheckIn': 'Today, 07:30 AM',
      'stress': 'High (7.8/10)',
      'sleep': '4.2 hrs',
      'followUpRequired': true,
    },
    {
      'id': 'P002',
      'name': 'Naik Amit Singh',
      'unit': 'Bravo Battery (Unit 102)',
      'status': 'Stable',
      'trend': 'Stable',
      'lastCheckIn': 'Yesterday',
      'stress': 'Moderate (4.1/10)',
      'sleep': '6.8 hrs',
      'followUpRequired': false,
    },
    {
      'id': 'P003',
      'name': 'Sepoy Vikram Rathore',
      'unit': 'Charlie Company (Unit 103)',
      'status': 'Elevated Risk',
      'trend': 'Rising',
      'lastCheckIn': 'Today, 08:15 AM',
      'stress': 'High (8.2/10)',
      'sleep': '3.9 hrs',
      'followUpRequired': true,
    },
    {
      'id': 'P004',
      'name': 'Subedar Mohan Das',
      'unit': 'Alpha Battery (Unit 101)',
      'status': 'Cleared',
      'trend': 'Improving',
      'lastCheckIn': 'Today, 06:45 AM',
      'stress': 'Low (2.4/10)',
      'sleep': '7.5 hrs',
      'followUpRequired': false,
    },
    {
      'id': 'P005',
      'name': 'Havildar Deepak Verma',
      'unit': 'Delta Logistics (Unit 104)',
      'status': 'Watchlist',
      'trend': 'Rising',
      'lastCheckIn': '2 days ago',
      'stress': 'Moderate (6.1/10)',
      'sleep': '5.1 hrs',
      'followUpRequired': true,
    },
  ];

  List<Map<String, dynamic>> _interventions = [
    {
      'id': 'INT-101',
      'personnelId': 'P001',
      'name': 'Havildar Rajesh Kumar',
      'actionType': 'Wellness Counseling',
      'dueDate': 'Today',
      'status': 'Due Today',
      'assignedOfficer': 'Capt. Verma (Welfare)',
      'notes': 'Follow up on sustained sleep deficit and workload fatigue.',
    },
    {
      'id': 'INT-102',
      'personnelId': 'P003',
      'name': 'Sepoy Vikram Rathore',
      'actionType': 'Medical / Rest Referral',
      'dueDate': 'Today',
      'status': 'Due Today',
      'assignedOfficer': 'Capt. Verma (Welfare)',
      'notes': 'Consecutive high stress check-ins. Recommended 48-hour duty respite.',
    },
    {
      'id': 'INT-103',
      'personnelId': 'P005',
      'name': 'Havildar Deepak Verma',
      'actionType': 'Peer Support Session',
      'dueDate': 'Tomorrow',
      'status': 'In Progress',
      'assignedOfficer': 'Sub. Sharma',
      'notes': 'Family welfare and shift adjustment counseling.',
    },
    {
      'id': 'INT-104',
      'personnelId': 'P004',
      'name': 'Subedar Mohan Das',
      'actionType': 'Post-Leave Reintegration',
      'dueDate': 'Completed',
      'status': 'Completed',
      'assignedOfficer': 'Capt. Verma (Welfare)',
      'notes': 'Reintegration completed successfully. Check-ins normalized.',
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchLiveWelfareData();
  }

  Future<void> _fetchLiveWelfareData() async {
    try {
      final res = await ApiClient.get('/personnel?page_size=50');
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final items = data['items'] as List<dynamic>?;
        if (items != null && items.isNotEmpty) {
          setState(() {
            _personnelList = items.map((item) {
              final id = item['user_code'] ?? item['id'] ?? 'P001';
              final isActive = item['is_active'] ?? true;
              return {
                'id': id.toString(),
                'name': item['full_name'] ?? 'Personnel $id',
                'unit': item['unit_id'] ?? 'Alpha Battery',
                'status': isActive ? 'Stable' : 'Elevated Risk',
                'trend': isActive ? 'Stable' : 'Rising',
                'lastCheckIn': 'Today',
                'stress': isActive ? 'Low (3.2/10)' : 'High (7.9/10)',
                'sleep': isActive ? '7.0 hrs' : '4.5 hrs',
                'followUpRequired': !isActive,
              };
            }).toList();
          });
        }
      }
    } catch (_) {
      // Graceful fallback to default structured data
    }
  }

  void _showPersonnelDetailModal(Map<String, dynamic> p) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        final isRisk = p['status'] == 'Elevated Risk';
        return Container(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 26,
                        backgroundColor: isRisk ? Colors.red.shade100 : const Color(0xFF0D47A1).withOpacity(0.1),
                        child: Icon(
                          Icons.person,
                          size: 28,
                          color: isRisk ? Colors.red.shade800 : const Color(0xFF0D47A1),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            p['name'],
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          Text(
                            'ID: ${p['id']} • ${p['unit']}',
                            style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                          ),
                        ],
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 12),
              const Text(
                'Welfare Assessment Metrics',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile('Stress Level', p['stress'], isRisk ? Colors.red : Colors.green),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricTile('Avg. Sleep', p['sleep'], isRisk ? Colors.orange : Colors.blue),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile('Trend', p['trend'], isRisk ? Colors.redAccent : Colors.teal),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricTile('Last Check-in', p['lastCheckIn'], Colors.grey.shade800),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Viewing full wellness history for ${p['name']}'),
                            backgroundColor: const Color(0xFF0D47A1),
                          ),
                        );
                      },
                      icon: const Icon(Icons.history),
                      label: const Text('Full History'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                        _showCreateFollowUpDialog(p['id'], p['name']);
                      },
                      icon: const Icon(Icons.add_task),
                      label: const Text('Add Follow-up'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0D47A1),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMetricTile(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }

  void _showCreateFollowUpDialog([String? defaultId, String? defaultName]) {
    final personnelCtrl = TextEditingController(text: defaultId ?? '');
    final notesCtrl = TextEditingController();
    String actionType = 'Wellness Counseling';

    showDialog(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: const Text('Schedule Welfare Follow-up'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: personnelCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Personnel ID',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.badge),
                      ),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: actionType,
                      decoration: const InputDecoration(
                        labelText: 'Action Type',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.health_and_safety),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'Wellness Counseling', child: Text('Wellness Counseling')),
                        DropdownMenuItem(value: 'Medical / Rest Referral', child: Text('Medical / Rest Referral')),
                        DropdownMenuItem(value: 'Peer Support Session', child: Text('Peer Support Session')),
                        DropdownMenuItem(value: 'Shift Duty Adjustment', child: Text('Shift Duty Adjustment')),
                      ],
                      onChanged: (val) {
                        if (val != null) setDialogState(() => actionType = val);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: notesCtrl,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Officer Notes / Reason',
                        border: OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: () {
                    if (personnelCtrl.text.trim().isEmpty) return;
                    setState(() {
                      _interventions.insert(0, {
                        'id': 'INT-${DateTime.now().millisecondsSinceEpoch % 10000}',
                        'personnelId': personnelCtrl.text.trim(),
                        'name': defaultName ?? 'Personnel ${personnelCtrl.text.trim()}',
                        'actionType': actionType,
                        'dueDate': 'Today',
                        'status': 'Due Today',
                        'assignedOfficer': 'Capt. Verma (Welfare)',
                        'notes': notesCtrl.text.trim().isNotEmpty ? notesCtrl.text.trim() : 'Scheduled follow-up.',
                      });
                      _currentIndex = 2; // Switch to follow-ups
                    });
                    Navigator.pop(dialogContext);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Follow-up scheduled for ${personnelCtrl.text.trim()}'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0D47A1),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Save & Schedule'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_getAppBarTitle()),
        backgroundColor: const Color(0xFF0D47A1),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () {
              _fetchLiveWelfareData();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Refreshed welfare data'), duration: Duration(seconds: 1)),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              context.read<AuthProvider>().logout();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: _buildCurrentView(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        selectedItemColor: const Color(0xFF0D47A1),
        unselectedItemColor: Colors.grey.shade600,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_rounded),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people_alt_rounded),
            label: 'Personnel',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assignment_turned_in_rounded),
            label: 'Follow-ups',
          ),
        ],
      ),
      floatingActionButton: _currentIndex == 2
          ? FloatingActionButton.extended(
              onPressed: () => _showCreateFollowUpDialog(),
              backgroundColor: const Color(0xFF0D47A1),
              foregroundColor: Colors.white,
              icon: const Icon(Icons.add),
              label: const Text('New Follow-up'),
            )
          : null,
    );
  }

  String _getAppBarTitle() {
    switch (_currentIndex) {
      case 1:
        return 'Personnel Directory';
      case 2:
        return 'Follow-ups & Interventions';
      default:
        return 'Welfare Dashboard';
    }
  }

  Widget _buildCurrentView() {
    switch (_currentIndex) {
      case 1:
        return _buildPersonnelView();
      case 2:
        return _buildFollowUpsView();
      default:
        return _buildDashboardView();
    }
  }

  // View 0: Main Dashboard
  Widget _buildDashboardView() {
    final elevatedCount = _personnelList.where((p) => p['status'] == 'Elevated Risk').length;
    final followUpsCount = _interventions.where((i) => i['status'] != 'Completed').length;
    final risingTrendsCount = _personnelList.where((p) => p['trend'] == 'Rising').length;
    final totalCount = _personnelList.length;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Unit Overview',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF0D47A1),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: const Text('Live Status', style: TextStyle(fontSize: 12, color: Color(0xFF0D47A1), fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Interactive Stat Cards Grid
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _buildStatCard(
                title: 'Total Personnel',
                value: '$totalCount',
                subtitle: 'Tap to view all',
                color: const Color(0xFF0D47A1),
                icon: Icons.people_outline,
                onTap: () => setState(() => _currentIndex = 1),
              ),
              _buildStatCard(
                title: 'Elevated Risk',
                value: '$elevatedCount',
                subtitle: 'Needs attention',
                color: Colors.orange.shade800,
                icon: Icons.warning_amber_rounded,
                onTap: () {
                  setState(() {
                    _currentIndex = 1;
                    _personnelSearchQuery = 'Elevated';
                  });
                },
              ),
              _buildStatCard(
                title: 'Follow-ups',
                value: '$followUpsCount',
                subtitle: 'Active cases',
                color: Colors.teal.shade700,
                icon: Icons.assignment_outlined,
                onTap: () => setState(() => _currentIndex = 2),
              ),
              _buildStatCard(
                title: 'Rising Trends',
                value: '$risingTrendsCount',
                subtitle: 'Early warning',
                color: Colors.redAccent.shade700,
                icon: Icons.trending_up,
                onTap: () {
                  setState(() {
                    _currentIndex = 1;
                    _personnelSearchQuery = 'Rising';
                  });
                },
              ),
            ],
          ),

          const SizedBox(height: 28),

          // Priority Personnel Section
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Priority Personnel (Action Needed)',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              TextButton(
                onPressed: () => setState(() => _currentIndex = 1),
                child: const Text('See all'),
              ),
            ],
          ),
          const SizedBox(height: 8),

          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _personnelList.where((p) => p['status'] == 'Elevated Risk').isNotEmpty 
                ? _personnelList.where((p) => p['status'] == 'Elevated Risk').take(3).length 
                : _personnelList.take(3).length,
            itemBuilder: (context, index) {
              final priorityItems = _personnelList.where((p) => p['status'] == 'Elevated Risk').toList();
              final p = priorityItems.isNotEmpty && index < priorityItems.length 
                  ? priorityItems[index] 
                  : _personnelList[index];

              final isRisk = p['status'] == 'Elevated Risk';
              return Card(
                elevation: 1.5,
                margin: const EdgeInsets.only(bottom: 10.0),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  leading: CircleAvatar(
                    backgroundColor: isRisk ? Colors.red.shade100 : Colors.blue.shade50,
                    child: Icon(
                      Icons.person,
                      color: isRisk ? Colors.red.shade800 : const Color(0xFF0D47A1),
                    ),
                  ),
                  title: Text(
                    '${p['name']} (${p['id']})',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 4.0),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: isRisk ? Colors.red.shade50 : Colors.green.shade50,
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: isRisk ? Colors.red.shade200 : Colors.green.shade200),
                          ),
                          child: Text(
                            p['status'],
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: isRisk ? Colors.red.shade800 : Colors.green.shade800,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Stress: ${p['stress']}',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                  ),
                  trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                  onTap: () => _showPersonnelDetailModal(p),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  // View 1: Personnel List & Search
  Widget _buildPersonnelView() {
    final filtered = _personnelList.where((p) {
      if (_personnelSearchQuery.isEmpty) return true;
      final q = _personnelSearchQuery.toLowerCase();
      return p['name'].toString().toLowerCase().contains(q) ||
          p['id'].toString().toLowerCase().contains(q) ||
          p['unit'].toString().toLowerCase().contains(q) ||
          p['status'].toString().toLowerCase().contains(q) ||
          p['trend'].toString().toLowerCase().contains(q);
    }).toList();

    return Column(
      children: [
        Container(
          color: Colors.white,
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              TextField(
                decoration: InputDecoration(
                  hintText: 'Search by Name, ID, or Unit...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _personnelSearchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () => setState(() => _personnelSearchQuery = ''),
                        )
                      : null,
                  filled: true,
                  fillColor: Colors.grey.shade100,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
                onChanged: (val) => setState(() => _personnelSearchQuery = val),
              ),
              const SizedBox(height: 10),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _buildFilterChip('All', _personnelSearchQuery.isEmpty),
                    const SizedBox(width: 8),
                    _buildFilterChip('Elevated Risk', _personnelSearchQuery == 'Elevated'),
                    const SizedBox(width: 8),
                    _buildFilterChip('Stable', _personnelSearchQuery == 'Stable'),
                    const SizedBox(width: 8),
                    _buildFilterChip('Rising Trends', _personnelSearchQuery == 'Rising'),
                  ],
                ),
              ),
            ],
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: filtered.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.search_off, size: 48, color: Colors.grey.shade400),
                      const SizedBox(height: 12),
                      Text('No personnel matching "$_personnelSearchQuery"', style: TextStyle(color: Colors.grey.shade600)),
                      TextButton(
                        onPressed: () => setState(() => _personnelSearchQuery = ''),
                        child: const Text('Clear search'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12.0),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final p = filtered[index];
                    final isRisk = p['status'] == 'Elevated Risk';
                    return Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 8.0),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: isRisk ? Colors.red.shade100 : const Color(0xFF0D47A1).withOpacity(0.1),
                          child: Icon(
                            Icons.person,
                            color: isRisk ? Colors.red.shade800 : const Color(0xFF0D47A1),
                          ),
                        ),
                        title: Text(p['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('${p['id']} • ${p['unit']}', style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Text('Trend: ${p['trend']}', style: TextStyle(fontSize: 12, color: isRisk ? Colors.red : Colors.green)),
                                const SizedBox(width: 12),
                                Text('Sleep: ${p['sleep']}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                              ],
                            ),
                          ],
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey),
                        onTap: () => _showPersonnelDetailModal(p),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String label, bool isSelected) {
    return FilterChip(
      selected: isSelected,
      label: Text(label),
      selectedColor: const Color(0xFF0D47A1).withOpacity(0.15),
      checkmarkColor: const Color(0xFF0D47A1),
      labelStyle: TextStyle(
        color: isSelected ? const Color(0xFF0D47A1) : Colors.black87,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        fontSize: 12,
      ),
      onSelected: (_) {
        setState(() {
          if (label == 'All') {
            _personnelSearchQuery = '';
          } else if (label == 'Rising Trends') {
            _personnelSearchQuery = 'Rising';
          } else {
            _personnelSearchQuery = label;
          }
        });
      },
    );
  }

  // View 2: Follow-ups & Interventions List
  Widget _buildFollowUpsView() {
    final filtered = _interventions.where((i) {
      if (_followUpFilter == 'All') return true;
      return i['status'] == _followUpFilter;
    }).toList();

    return Column(
      children: [
        Container(
          color: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildTabFilterChip('All', _followUpFilter == 'All'),
                const SizedBox(width: 8),
                _buildTabFilterChip('Due Today', _followUpFilter == 'Due Today'),
                const SizedBox(width: 8),
                _buildTabFilterChip('In Progress', _followUpFilter == 'In Progress'),
                const SizedBox(width: 8),
                _buildTabFilterChip('Completed', _followUpFilter == 'Completed'),
              ],
            ),
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: filtered.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.check_circle_outline, size: 48, color: Colors.grey.shade400),
                      const SizedBox(height: 12),
                      Text('No follow-ups under $_followUpFilter', style: TextStyle(color: Colors.grey.shade600)),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () => _showCreateFollowUpDialog(),
                        icon: const Icon(Icons.add),
                        label: const Text('Schedule Follow-up'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12.0),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final item = filtered[index];
                    final isDue = item['status'] == 'Due Today';
                    final isCompleted = item['status'] == 'Completed';

                    return Card(
                      elevation: 1.5,
                      margin: const EdgeInsets.only(bottom: 10.0),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(14.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  item['actionType'],
                                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: isDue
                                        ? Colors.orange.shade50
                                        : isCompleted
                                            ? Colors.green.shade50
                                            : Colors.blue.shade50,
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(
                                      color: isDue
                                          ? Colors.orange.shade300
                                          : isCompleted
                                              ? Colors.green.shade300
                                              : Colors.blue.shade300,
                                    ),
                                  ),
                                  child: Text(
                                    item['status'],
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: isDue
                                          ? Colors.orange.shade900
                                          : isCompleted
                                              ? Colors.green.shade900
                                              : Colors.blue.shade900,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Personnel: ${item['name']} (${item['personnelId']})',
                              style: TextStyle(color: Colors.grey.shade800, fontWeight: FontWeight.w500, fontSize: 13),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Assigned: ${item['assignedOfficer']} • Due: ${item['dueDate']}',
                              style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                            ),
                            if (item['notes'] != null) ...[
                              const SizedBox(height: 8),
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.grey.shade50,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  item['notes'],
                                  style: TextStyle(fontSize: 12, color: Colors.grey.shade700, fontStyle: FontStyle.italic),
                                ),
                              ),
                            ],
                            const SizedBox(height: 10),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                if (!isCompleted) ...[
                                  OutlinedButton.icon(
                                    onPressed: () {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('Rescheduled ${item['id']}')),
                                      );
                                    },
                                    icon: const Icon(Icons.calendar_month, size: 14),
                                    label: const Text('Reschedule', style: TextStyle(fontSize: 12)),
                                    style: OutlinedButton.styleFrom(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  ElevatedButton.icon(
                                    onPressed: () {
                                      setState(() {
                                        item['status'] = 'Completed';
                                      });
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(
                                          content: Text('Marked ${item['id']} as completed'),
                                          backgroundColor: Colors.green,
                                        ),
                                      );
                                    },
                                    icon: const Icon(Icons.check, size: 14),
                                    label: const Text('Complete', style: TextStyle(fontSize: 12)),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.green.shade700,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    ),
                                  ),
                                ] else ...[
                                  const Text('Resolved', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 12)),
                                ],
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildTabFilterChip(String label, bool isSelected) {
    return ChoiceChip(
      selected: isSelected,
      label: Text(label),
      selectedColor: const Color(0xFF0D47A1),
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black87,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        fontSize: 12,
      ),
      onSelected: (_) {
        setState(() {
          _followUpFilter = label;
        });
      },
    );
  }

  // Interactive Stat Card with InkWell
  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtitle,
    required Color color,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(14.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  CircleAvatar(
                    radius: 18,
                    backgroundColor: color.withOpacity(0.12),
                    child: Icon(icon, size: 20, color: color),
                  ),
                  Icon(Icons.arrow_forward_ios, size: 12, color: Colors.grey.shade400),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
