import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function Home() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      fetchUser(savedToken);
    }
  }, []);

  const fetchUser = async (token) => {
    try {
      const res = await axios.get(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(res.data);
    } catch (err) {
      localStorage.removeItem('token');
      setToken(null);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const res = await axios.post(`${API_URL}/token`, formData);
      localStorage.setItem('token', res.data.access_token);
      setToken(res.data.access_token);
      fetchUser(res.data.access_token);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  const handleRegister = async () => {
    try {
      await axios.post(`${API_URL}/register`, {
        email,
        password,
        full_name: 'Test User'
      });
      alert('Registration successful! Please login.');
      setShowLogin(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
          <h1 className="text-3xl font-bold text-center mb-2">aman ga?</h1>
          <p className="text-center text-gray-600 mb-6">Tanya dulu, transfer kemudian.</p>

          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border rounded-lg p-3"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border rounded-lg p-3"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-green-500 text-white py-3 rounded-lg font-bold hover:bg-green-600"
            >
              {showLogin ? 'Login' : 'Register'}
            </button>
          </form>

          <button
            onClick={() => setShowLogin(!showLogin)}
            className="w-full mt-4 text-green-600 hover:underline"
          >
            {showLogin ? 'Need an account? Register' : 'Have an account? Login'}
          </button>

          {!showLogin && (
            <button
              onClick={handleRegister}
              className="w-full mt-2 bg-blue-500 text-white py-3 rounded-lg font-bold hover:bg-blue-600"
            >
              Create Account
            </button>
          )}

          <div className="mt-6 text-xs text-gray-500 text-center">
            <p>Demo Credentials:</p>
            <p>Admin: admin@amanga.id / admin123</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-green-600">aman ga?</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">{user?.email}</span>
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
        {user?.role === 'ADMIN' || user?.role === 'FINANCE' ? (
          <AdminDashboard token={token} />
        ) : (
          <UserDashboard token={token} user={user} />
        )}
      </main>
    </div>
  );
}

function UserDashboard({ token, user }) {
  const [credits, setCredits] = useState([]);
  const [showPayment, setShowPayment] = useState(false);

  useEffect(() => {
    fetchCredits();
  }, []);

  const fetchCredits = async () => {
    const res = await axios.get(`${API_URL}/payment/credits`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setCredits(res.data);
  };

  const services = [
    { type: 'CEK_DASAR', name: 'Cek Dasar', price: 1000, desc: 'OJK/Kominfo check', auto: true },
    { type: 'CEK_DEEP', name: 'Cek Deep', price: 15000, desc: 'AI chat analysis', auto: false },
    { type: 'CEK_PLUS', name: 'Cek Plus', price: 45000, desc: 'Contract + legal letter', auto: false },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* Service Credits */}
      <div className="bg-white rounded-xl p-6 shadow-lg mb-6">
        <h3 className="text-xl font-bold mb-4">Layanan Anda</h3>
        {credits.length === 0 ? (
          <p className="text-gray-500">Belum ada layanan aktif. Silakan purchase.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {credits.map((credit) => (
              <div key={credit.id} className="border rounded-lg p-4">
                <p className="font-bold">{credit.service_type}</p>
                <p className="text-sm text-gray-600">
                  {credit.used_quantity}/{credit.quantity} digunakan
                </p>
                <button
                  onClick={async () => {
                    await axios.get(`${API_URL}/service/use/${credit.service_type}`, {
                      headers: { Authorization: `Bearer ${token}` }
                    });
                    alert('Service activated! Check console for mock result.');
                    fetchCredits();
                  }}
                  className="mt-2 bg-green-500 text-white px-4 py-2 rounded text-sm hover:bg-green-600"
                >
                  Gunakan
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Purchase Services */}
      <div className="bg-white rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4">Beli Layanan</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {services.map((service) => (
            <div key={service.type} className="border rounded-lg p-4 hover:shadow-lg transition">
              <h4 className="font-bold text-lg">{service.name}</h4>
              <p className="text-2xl font-bold text-green-600 my-2">
                Rp {service.price.toLocaleString('id-ID')}
              </p>
              <p className="text-sm text-gray-600 mb-4">{service.desc}</p>
              {service.auto && (
                <p className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded inline-block mb-4">
                  ⚡ Aktivasi Otomatis
                </p>
              )}
              {!service.auto && (
                <p className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded inline-block mb-4">
                  ⏳ Verifikasi Manual (5-30 menit)
                </p>
              )}
              <button
                onClick={() => setShowPayment(service)}
                className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
              >
                Beli Sekarang
              </button>
            </div>
          ))}
        </div>
      </div>

      {showPayment && (
        <PaymentModal
          service={showPayment}
          token={token}
          onClose={() => setShowPayment(false)}
          onPurchaseComplete={fetchCredits}
        />
      )}
    </div>
  );
}

function AdminDashboard({ token }) {
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    fetchPendingPayments();
    const interval = setInterval(fetchPendingPayments, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchPendingPayments = async () => {
    const res = await axios.get(`${API_URL}/admin/payments/pending`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setPayments(res.data);
  };

  const handleApprove = async (paymentId) => {
    await axios.post(`${API_URL}/admin/payment/${paymentId}/approve`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPendingPayments();
    alert('Payment approved!');
  };

  const handleReject = async (paymentId) => {
    const reason = prompt('Reason for rejection:');
    if (!reason) return;
    await axios.post(`${API_URL}/admin/payment/${paymentId}/reject?reason=${encodeURIComponent(reason)}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPendingPayments();
    alert('Payment rejected!');
  };

  const handleFlag = async (paymentId) => {
    const flagType = prompt('Flag type (FAKE_PROOF, DUPLICATE_PROOF, etc.):');
    if (!flagType) return;
    await axios.post(`${API_URL}/admin/payment/${paymentId}/flag?flag_type=${flagType}&severity=CRITICAL`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPendingPayments();
    alert('User suspended!');
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Admin Dashboard</h2>

      <div className="bg-white rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4">Pembayaran Pending ({payments.length})</h3>
        
        {payments.length === 0 ? (
          <p className="text-gray-500">Tidak ada pembayaran pending.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">User</th>
                  <th className="px-4 py-2 text-left">Service</th>
                  <th className="px-4 py-2 text-left">Amount</th>
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Time</th>
                  <th className="px-4 py-2 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.id} className="border-t">
                    <td className="px-4 py-2">{payment.users?.email}</td>
                    <td className="px-4 py-2">{payment.service_type}</td>
                    <td className="px-4 py-2">Rp {payment.amount.toLocaleString('id-ID')}</td>
                    <td className="px-4 py-2">
                      {payment.service_type === 'CEK_DASAR' ? (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">AUTO</span>
                      ) : (
                        <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">MANUAL</span>
                      )}
                    </td>
                    <td className="px-4 py-2">{new Date(payment.created_at).toLocaleString('id-ID')}</td>
                    <td className="px-4 py-2">
                      <button
                        onClick={() => handleApprove(payment.id)}
                        className="bg-green-500 text-white px-3 py-1 rounded mr-2 hover:bg-green-600"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleReject(payment.id)}
                        className="bg-red-500 text-white px-3 py-1 rounded mr-2 hover:bg-red-600"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleFlag(payment.id)}
                        className="bg-orange-500 text-white px-3 py-1 rounded hover:bg-orange-600"
                      >
                        Flag Fraud
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function PaymentModal({ service, token, onClose, onPurchaseComplete }) {
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    transaction_id: '',
    bank_name: 'BCA',
    transaction_date: new Date().toISOString().slice(0, 16)
  });
  const [proofImage, setProofImage] = useState(null);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);

    const form = new FormData();
    form.append('service_type', service.type);
    form.append('amount', service.price);
    form.append('payment_method', 'BANK_TRANSFER');
    form.append('bank_name', formData.bank_name);
    form.append('transaction_id', formData.transaction_id);
    form.append('transaction_date', formData.transaction_date);
    form.append('proof_image', proofImage);

    try {
      const res = await axios.post(`${API_URL}/payment/upload`, form, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setMessage({
        type: res.data.status === 'AUTO_APPROVED' ? 'success' : 'info',
        text: res.data.message
      });

      onPurchaseComplete();
      setTimeout(onClose, 3000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Upload failed'
      });
    }

    setUploading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
        <h3 className="text-xl font-bold mb-4">Upload Bukti Pembayaran</h3>

        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <p className="font-bold">{service.name}</p>
          <p className="text-2xl text-green-600">Rp {service.price.toLocaleString('id-ID')}</p>
          {service.auto ? (
            <p className="text-sm text-green-600 mt-2">⚡ Aktivasi Otomatis</p>
          ) : (
            <p className="text-sm text-yellow-600 mt-2">⏳ Verifikasi 5-30 menit</p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Screenshot Transfer</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setProofImage(e.target.files[0])}
              className="w-full border rounded-lg p-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">ID Transaksi</label>
            <input
              type="text"
              value={formData.transaction_id}
              onChange={(e) => setFormData({...formData, transaction_id: e.target.value})}
              className="w-full border rounded-lg p-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Bank</label>
            <select
              value={formData.bank_name}
              onChange={(e) => setFormData({...formData, bank_name: e.target.value})}
              className="w-full border rounded-lg p-2"
            >
              <option value="BCA">BCA</option>
              <option value="MANDIRI">Mandiri</option>
              <option value="BNI">BNI</option>
              <option value="BRI">BRI</option>
              <option value="DANA">DANA</option>
              <option value="GOPAY">GoPay</option>
              <option value="OVO">OVO</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Tanggal Transaksi</label>
            <input
              type="datetime-local"
              value={formData.transaction_date}
              onChange={(e) => setFormData({...formData, transaction_date: e.target.value})}
              className="w-full border rounded-lg p-2"
              required
            />
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 border rounded-lg"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={uploading}
              className="flex-1 py-3 bg-green-500 text-white rounded-lg disabled:opacity-50"
            >
              {uploading ? 'Uploading...' : 'Konfirmasi'}
            </button>
          </div>

          {message && (
            <div className={`p-3 rounded-lg text-center ${
              message.type === 'success' ? 'bg-green-50 text-green-700' :
              message.type === 'error' ? 'bg-red-50 text-red-700' :
              'bg-yellow-50 text-yellow-700'
            }`}>
              {message.text}
            </div>
          )}

          <p className="text-xs text-gray-500 text-center">
            ⚠️ Bukti palsu akan terdeteksi. Akun akan di-suspend.
          </p>
        </form>
      </div>
    </div>
  );
}
