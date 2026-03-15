import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AdminDashboard({ token }) {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    pending: 0,
    approvedToday: 0,
    rejectedToday: 0,
    fraudFlags: 0
  });
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchPendingPayments();
    
    if (autoRefresh) {
      const interval = setInterval(fetchPendingPayments, 30000); // Poll every 30s
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchPendingPayments = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/payments/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPayments(res.data);
      updateStats(res.data);
    } catch (err) {
      console.error('Failed to fetch payments:', err);
    }
    setLoading(false);
  };

  const updateStats = (pendingPayments) => {
    setStats(prev => ({
      ...prev,
      pending: pendingPayments.length
    }));
  };

  const handleApprove = async (paymentId) => {
    const notes = prompt('Add verification notes (optional):') || '';
    
    try {
      await axios.post(`${API_URL}/admin/payment/${paymentId}/approve?notes=${encodeURIComponent(notes)}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('✅ Payment approved!');
      fetchPendingPayments();
    } catch (err) {
      alert('Failed to approve: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleReject = async (paymentId) => {
    const reason = prompt('Reason for rejection (required):');
    if (!reason) return;
    
    try {
      await axios.post(`${API_URL}/admin/payment/${paymentId}/reject?reason=${encodeURIComponent(reason)}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('❌ Payment rejected');
      fetchPendingPayments();
    } catch (err) {
      alert('Failed to reject: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleFlag = async (paymentId) => {
    const flagType = prompt('Flag type:\n- FAKE_PROOF\n- DUPLICATE_PROOF\n- MANIPULATED_IMAGE\n- SUSPICIOUS_PATTERN');
    if (!flagType) return;
    
    const severity = prompt('Severity:\n- LOW\n- MEDIUM\n- HIGH\n- CRITICAL') || 'HIGH';
    
    try {
      await axios.post(`${API_URL}/admin/payment/${paymentId}/flag?flag_type=${flagType}&severity=${severity}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('🚩 User suspended and flagged for fraud!');
      fetchPendingPayments();
    } catch (err) {
      alert('Failed to flag: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleViewProof = (payment) => {
    // In production, this would open the actual image from storage
    alert(`Viewing proof for payment ${payment.id}\n\nIn production, this opens: ${payment.proof_image_url}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-xl">Loading payments...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Controls */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">
          Pending Payments ({payments.length})
        </h3>
        <div className="flex items-center gap-3">
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="mr-2"
            />
            Auto-refresh (30s)
          </label>
          <button
            onClick={fetchPendingPayments}
            className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 text-sm"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Payments Table */}
      {payments.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <div className="text-5xl mb-4">🎉</div>
          <p className="text-gray-500 text-lg">No pending payments!</p>
          <p className="text-gray-400 text-sm mt-2">All caught up. Great job!</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-50 border-b-2 border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Payment
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {payments.map((payment) => (
                <tr key={payment.id} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-4">
                    <div>
                      <p className="font-medium text-gray-900">
                        {payment.users?.full_name || payment.users?.email}
                      </p>
                      <p className="text-sm text-gray-500">{payment.users?.email}</p>
                      {payment.users?.phone && (
                        <p className="text-xs text-gray-400">{payment.users?.phone}</p>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-medium">{payment.service_type.replace('_', ' ')}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-bold text-green-600">
                      Rp {payment.amount.toLocaleString('id-ID')}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <div>
                      <p className="text-sm">{payment.payment_method}</p>
                      <p className="text-xs text-gray-500">{payment.bank_name}</p>
                      <p className="text-xs text-gray-400 truncate max-w-[150px]">
                        ID: {payment.transaction_id}
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="text-sm text-gray-500">
                      {new Date(payment.created_at).toLocaleDateString('id-ID')}
                      <br />
                      {new Date(payment.created_at).toLocaleTimeString('id-ID', {hour: '2-digit', minute:'2-digit'})}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => handleViewProof(payment)}
                        className="bg-blue-500 text-white px-3 py-1.5 rounded-lg hover:bg-blue-600 text-sm transition"
                        title="View Proof"
                      >
                        👁️ Proof
                      </button>
                      <button
                        onClick={() => handleApprove(payment.id)}
                        className="bg-green-500 text-white px-3 py-1.5 rounded-lg hover:bg-green-600 text-sm transition"
                        title="Approve"
                      >
                        ✅ Approve
                      </button>
                      <button
                        onClick={() => handleReject(payment.id)}
                        className="bg-red-500 text-white px-3 py-1.5 rounded-lg hover:bg-red-600 text-sm transition"
                        title="Reject"
                      >
                        ❌ Reject
                      </button>
                      <button
                        onClick={() => handleFlag(payment.id)}
                        className="bg-orange-500 text-white px-3 py-1.5 rounded-lg hover:bg-orange-600 text-sm transition"
                        title="Flag as Fraud"
                      >
                        🚩 Flag
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Quick Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-yellow-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          <div className="text-sm text-yellow-700">Pending</div>
        </div>
        <div className="bg-green-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{stats.approvedToday}</div>
          <div className="text-sm text-green-700">Approved Today</div>
        </div>
        <div className="bg-red-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{stats.rejectedToday}</div>
          <div className="text-sm text-red-700">Rejected Today</div>
        </div>
        <div className="bg-orange-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">{stats.fraudFlags}</div>
          <div className="text-sm text-orange-700">Fraud Flags</div>
        </div>
      </div>
    </div>
  );
}
