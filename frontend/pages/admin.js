import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import AdminDashboard from '../components/AdminDashboard';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Admin() {
  const router = useRouter();
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (!savedToken) {
      router.push('/');
      return;
    }
    setToken(savedToken);
    fetchUser(savedToken);
  }, []);

  const fetchUser = async (token) => {
    try {
      const res = await axios.get(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.data.role !== 'ADMIN' && res.data.role !== 'FINANCE') {
        alert('Access denied. Admin role required.');
        router.push('/dashboard');
        return;
      }
      
      setUser(res.data);
      setLoading(false);
    } catch (err) {
      localStorage.removeItem('token');
      router.push('/');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-green-600">aman ga?</h1>
            <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
              👑 Admin Panel
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 hidden md:block">{user?.email}</span>
            <a
              href="/dashboard"
              className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
            >
              User View
            </a>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Admin Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold text-blue-600" id="validation-count">128</div>
            <div className="text-gray-500">Total Validations</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold text-green-600" id="authentic-count">98</div>
            <div className="text-gray-500">Authentic Receipts</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold text-red-600" id="suspicious-count">30</div>
            <div className="text-gray-500">Suspicious Receipts</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold text-orange-600" id="fraud-count">-</div>
            <div className="text-gray-500">Fraud Flags</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg mb-8">
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('validation')}
                className={`px-6 py-4 font-medium transition ${
                  activeTab === 'validation'
                    ? 'border-b-2 border-green-500 text-green-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                🔍 Receipt Validation
              </button>
              <button
                onClick={() => setActiveTab('fraud')}
                className={`px-6 py-4 font-medium transition ${
                  activeTab === 'fraud'
                    ? 'border-b-2 border-orange-500 text-orange-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                🚩 Fraud Reviews
              </button>
              <button
                onClick={() => setActiveTab('audit')}
                className={`px-6 py-4 font-medium transition ${
                  activeTab === 'audit'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                📋 Audit Log
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'validation' && <ValidationDashboard token={token} />}
            {activeTab === 'fraud' && <FraudReview token={token} />}
            {activeTab === 'audit' && <AuditLog token={token} />}
          </div>
        </div>
      </main>
    </div>
  );
}

function ValidationDashboard({ token }) {
  return (
    <div>
      <h3 className="text-xl font-bold mb-4">Receipt Validation Dashboard</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl p-6 shadow">
          <div className="text-3xl font-bold text-blue-600">128</div>
          <div className="text-gray-500">Total Validations</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow">
          <div className="text-3xl font-bold text-green-600">98</div>
          <div className="text-gray-500">Authentic Receipts</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow">
          <div className="text-3xl font-bold text-red-600">30</div>
          <div className="text-gray-500">Suspicious Receipts</div>
        </div>
      </div>
      
      <div className="bg-white rounded-xl p-6 shadow">
        <h4 className="font-bold mb-4">Recent Validations</h4>
        <p className="text-gray-500">No recent validations to display.</p>
      </div>
    </div>
  );
}

function FraudReview({ token }) {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFlags();
  }, []);

  const fetchFlags = async () => {
    try {
      // In production, create an endpoint for this
      setFlags([]);
    } catch (err) {
      console.error('Failed to fetch flags:', err);
    }
    setLoading(false);
  };

  const handleReview = async (flagId, status, action) => {
    try {
      await axios.post(`${API_URL}/admin/fraud/${flagId}/review`, {
        status,
        action_taken: action
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Review submitted!');
      fetchFlags();
    } catch (err) {
      alert('Failed to submit review');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h3 className="text-xl font-bold mb-4">Fraud Flag Reviews</h3>
      {flags.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No pending fraud reviews.
        </div>
      ) : (
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-2 text-left">User</th>
              <th className="px-4 py-2 text-left">Flag Type</th>
              <th className="px-4 py-2 text-left">Severity</th>
              <th className="px-4 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {flags.map((flag) => (
              <tr key={flag.id} className="border-t">
                <td className="px-4 py-2">{flag.users?.email}</td>
                <td className="px-4 py-2">{flag.flag_type}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    flag.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                    flag.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                    flag.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {flag.severity}
                  </span>
                </td>
                <td className="px-4 py-2">
                  <button
                    onClick={() => handleReview(flag.id, 'CONFIRMED', 'SUSPENSION')}
                    className="bg-orange-500 text-white px-3 py-1 rounded mr-2 hover:bg-orange-600"
                  >
                    Suspend
                  </button>
                  <button
                    onClick={() => handleReview(flag.id, 'FALSE_POSITIVE', 'NO_ACTION')}
                    className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                  >
                    Dismiss
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function AuditLog({ token }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // In production, fetch audit logs
    setLogs([]);
  }, []);

  return (
    <div>
      <h3 className="text-xl font-bold mb-4">Admin Audit Log</h3>
      {logs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No audit logs available.
        </div>
      ) : (
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-2 text-left">Admin</th>
              <th className="px-4 py-2 text-left">Action</th>
              <th className="px-4 py-2 text-left">Target</th>
              <th className="px-4 py-2 text-left">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-t">
                <td className="px-4 py-2">{log.admin_id}</td>
                <td className="px-4 py-2">{log.action}</td>
                <td className="px-4 py-2">{log.target_type}: {log.target_id}</td>
                <td className="px-4 py-2">{new Date(log.created_at).toLocaleString('id-ID')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
