import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import PaymentUpload from '../components/PaymentUpload';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Payment() {
  const router = useRouter();
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);

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
            <span className="text-gray-500">Payment History</span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="/dashboard"
              className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
            >
              Dashboard
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Payment History</h2>
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 font-medium"
          >
            + New Payment
          </button>
        </div>

        <PaymentHistory token={token} />

        {showUploadModal && (
          <PaymentUpload
            token={token}
            onClose={() => setShowUploadModal(false)}
            onSuccess={() => setShowUploadModal(false)}
          />
        )}
      </main>
    </div>
  );
}

function PaymentHistory({ token }) {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      const res = await axios.get(`${API_URL}/payment/my`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPayments(res.data);
    } catch (err) {
      console.error('Failed to fetch payments:', err);
    }
    setLoading(false);
  };

  const filteredPayments = payments.filter(payment => {
    if (filter === 'all') return true;
    return payment.status.toLowerCase() === filter.toLowerCase();
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'APPROVED':
      case 'AUTO_APPROVED':
        return 'bg-green-100 text-green-700';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-700';
      case 'REJECTED':
        return 'bg-red-100 text-red-700';
      case 'FLAGGED':
        return 'bg-orange-100 text-orange-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="bg-white rounded-xl shadow-lg">
      {/* Filters */}
      <div className="p-4 border-b flex gap-2">
        {['all', 'pending', 'approved', 'auto_approved', 'rejected', 'flagged'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === f
                ? 'bg-green-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f.replace('_', ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {/* Payment List */}
      {filteredPayments.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-5xl mb-4">💳</div>
          <p className="text-gray-500">No payments found.</p>
        </div>
      ) : (
        <div className="divide-y">
          {filteredPayments.map((payment) => (
            <div key={payment.id} className="p-4 hover:bg-gray-50 transition">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-bold text-lg">{payment.service_type.replace('_', ' ')}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(payment.status)}`}>
                      {payment.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="text-gray-400">Amount:</span> Rp {payment.amount.toLocaleString('id-ID')}
                    </div>
                    <div>
                      <span className="text-gray-400">Method:</span> {payment.payment_method}
                    </div>
                    <div>
                      <span className="text-gray-400">Transaction ID:</span> {payment.transaction_id}
                    </div>
                    <div>
                      <span className="text-gray-400">Date:</span> {new Date(payment.transaction_date).toLocaleString('id-ID')}
                    </div>
                  </div>
                  {payment.verification_notes && (
                    <div className="mt-3 p-3 bg-gray-100 rounded-lg">
                      <span className="text-gray-400 text-sm">Notes:</span>
                      <p className="text-gray-700">{payment.verification_notes}</p>
                    </div>
                  )}
                </div>
                <div className="ml-4">
                  {payment.proof_image_url && (
                    <a
                      href={payment.proof_image_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-600 hover:underline text-sm"
                    >
                      View Proof 📷
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
