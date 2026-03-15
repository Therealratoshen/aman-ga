import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import ServiceCard from '../components/ServiceCard';
import PaymentModal from '../components/PaymentUpload';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const router = useRouter();
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [credits, setCredits] = useState([]);
  const [payments, setPayments] = useState([]);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedService, setSelectedService] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (!savedToken) {
      router.push('/');
      return;
    }
    setToken(savedToken);
    fetchUser(savedToken);
  }, []);

  useEffect(() => {
    if (token) {
      fetchCredits();
      fetchPayments();
    }
  }, [token]);

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

  const fetchCredits = async () => {
    try {
      const res = await axios.get(`${API_URL}/payment/credits`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCredits(res.data);
    } catch (err) {
      console.error('Failed to fetch credits:', err);
    }
  };

  const fetchPayments = async () => {
    try {
      const res = await axios.get(`${API_URL}/payment/my`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPayments(res.data);
    } catch (err) {
      console.error('Failed to fetch payments:', err);
    }
  };

  const handlePurchase = (service) => {
    setSelectedService(service);
    setShowPaymentModal(true);
  };

  const handleUseService = async (serviceType) => {
    try {
      const res = await axios.get(`${API_URL}/service/use/${serviceType}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Service activated! Result:\n' + JSON.stringify(res.data.mock_result, null, 2));
      fetchCredits();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to use service');
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

  const services = [
    { type: 'CEK_DASAR', name: 'Cek Dasar', price: 1000, desc: 'OJK/Kominfo check', auto: true, color: 'green' },
    { type: 'CEK_DEEP', name: 'Cek Deep', price: 15000, desc: 'AI chat analysis', auto: false, color: 'blue' },
    { type: 'CEK_PLUS', name: 'Cek Plus', price: 45000, desc: 'Contract + legal letter', auto: false, color: 'purple' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-green-600">aman ga?</h1>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
              {user?.role}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 hidden md:block">{user?.email}</span>
            {(user?.role === 'ADMIN' || user?.role === 'FINANCE') && (
              <a
                href="/admin"
                className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
              >
                Admin Panel
              </a>
            )}
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
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 mb-8 text-white">
          <h2 className="text-2xl font-bold mb-2">Welcome, {user?.full_name || 'User'}! 👋</h2>
          <p className="opacity-90">Tanya dulu, transfer kemudian.</p>
        </div>

        {/* Service Credits Section */}
        <div className="bg-white rounded-xl p-6 shadow-lg mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold">Your Service Credits</h3>
            <span className="text-sm text-gray-500">{credits.length} active</span>
          </div>
          
          {credits.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">📦</div>
              <p className="text-gray-500">No active service credits yet.</p>
              <p className="text-sm text-gray-400">Purchase a service to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {credits.map((credit) => (
                <div key={credit.id} className="border rounded-xl p-4 hover:shadow-md transition">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-lg">{credit.service_type.replace('_', ' ')}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      credit.status === 'ACTIVE' ? 'bg-green-100 text-green-700' :
                      credit.status === 'USED' ? 'bg-gray-100 text-gray-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {credit.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    {credit.used_quantity}/{credit.quantity} used
                  </p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${(credit.used_quantity / credit.quantity) * 100}%` }}
                    ></div>
                  </div>
                  <button
                    onClick={() => handleUseService(credit.service_type)}
                    disabled={credit.used_quantity >= credit.quantity}
                    className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                  >
                    {credit.used_quantity >= credit.quantity ? 'Used Up' : 'Use Now'}
                  </button>
                  {credit.expires_at && (
                    <p className="text-xs text-gray-400 mt-2 text-center">
                      Expires: {new Date(credit.expires_at).toLocaleDateString('id-ID')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Purchase Services Section */}
        <div className="bg-white rounded-xl p-6 shadow-lg mb-8">
          <h3 className="text-xl font-bold mb-6">Purchase Services</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {services.map((service) => (
              <ServiceCard
                key={service.type}
                service={service}
                onPurchase={() => handlePurchase(service)}
              />
            ))}
          </div>
        </div>

        {/* Payment History Section */}
        <div className="bg-white rounded-xl p-6 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold">Payment History</h3>
            <span className="text-sm text-gray-500">{payments.length} payments</span>
          </div>
          
          {payments.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">📝</div>
              <p className="text-gray-500">No payment history yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Service</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Amount</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Method</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={payment.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3">{payment.service_type.replace('_', ' ')}</td>
                      <td className="px-4 py-3">Rp {payment.amount.toLocaleString('id-ID')}</td>
                      <td className="px-4 py-3">{payment.payment_method}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          payment.status === 'APPROVED' || payment.status === 'AUTO_APPROVED' ? 'bg-green-100 text-green-700' :
                          payment.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' :
                          payment.status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {payment.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(payment.created_at).toLocaleDateString('id-ID')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Payment Modal */}
      {showPaymentModal && selectedService && (
        <PaymentModal
          service={selectedService}
          token={token}
          onClose={() => {
            setShowPaymentModal(false);
            setSelectedService(null);
          }}
          onSuccess={() => {
            fetchCredits();
            fetchPayments();
          }}
        />
      )}
    </div>
  );
}
