import { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function PaymentUpload({ service, token, onClose, onSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    transaction_id: '',
    bank_name: 'BCA',
    transaction_date: new Date().toISOString().slice(0, 16)
  });
  const [proofImage, setProofImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    setMessage(null);

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

      onSuccess();
      setTimeout(onClose, 2000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Upload failed'
      });
    }

    setUploading(false);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProofImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Upload Payment Proof</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Service Info */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-bold text-lg">{service.name}</p>
              <p className="text-sm text-gray-600">{service.desc}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-green-600">
                Rp {service.price.toLocaleString('id-ID')}
              </p>
              {service.auto ? (
                <p className="text-xs text-green-600 mt-1">⚡ Auto-approve</p>
              ) : (
                <p className="text-xs text-yellow-600 mt-1">⏳ Manual review</p>
              )}
            </div>
          </div>
        </div>

        {/* Upload Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">
              📸 Screenshot of Transfer
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 text-center hover:border-green-500 transition">
              {imagePreview ? (
                <div>
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="max-h-48 mx-auto rounded-lg mb-2"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setProofImage(null);
                      setImagePreview(null);
                    }}
                    className="text-sm text-red-500 hover:underline"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div>
                  <div className="text-4xl mb-2">📁</div>
                  <p className="text-sm text-gray-600 mb-2">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-400">
                    PNG, JPG up to 5MB
                  </p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    required
                  />
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="mt-2 w-full text-sm text-gray-500"
                required
              />
            </div>
          </div>

          {/* Transaction ID */}
          <div>
            <label className="block text-sm font-medium mb-1">
              🔖 Transaction ID / Reference Number
            </label>
            <input
              type="text"
              value={formData.transaction_id}
              onChange={(e) => setFormData({...formData, transaction_id: e.target.value})}
              className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="e.g., TRX123456789"
              required
            />
          </div>

          {/* Bank Selection */}
          <div>
            <label className="block text-sm font-medium mb-1">
              🏦 Bank / E-Wallet
            </label>
            <select
              value={formData.bank_name}
              onChange={(e) => setFormData({...formData, bank_name: e.target.value})}
              className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="BCA">BCA</option>
              <option value="MANDIRI">Mandiri</option>
              <option value="BNI">BNI</option>
              <option value="BRI">BRI</option>
              <option value="DANA">DANA</option>
              <option value="GOPAY">GoPay</option>
              <option value="OVO">OVO</option>
              <option value="LINKAJA">LinkAja</option>
            </select>
          </div>

          {/* Transaction Date */}
          <div>
            <label className="block text-sm font-medium mb-1">
              📅 Transaction Date & Time
            </label>
            <input
              type="datetime-local"
              value={formData.transaction_date}
              onChange={(e) => setFormData({...formData, transaction_date: e.target.value})}
              className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            />
          </div>

          {/* Message */}
          {message && (
            <div className={`p-4 rounded-xl text-center ${
              message.type === 'success' ? 'bg-green-50 text-green-700' :
              message.type === 'error' ? 'bg-red-50 text-red-700' :
              'bg-blue-50 text-blue-700'
            }`}>
              {message.type === 'success' && '✅ '}
              {message.type === 'error' && '❌ '}
              {message.type === 'info' && '⏳ '}
              {message.text}
            </div>
          )}

          {/* Warning */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3">
            <p className="text-xs text-yellow-700">
              ⚠️ <strong>Warning:</strong> Fake or manipulated proof will be detected. 
              Your account will be suspended permanently.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={uploading}
              className="flex-1 py-3 border rounded-xl hover:bg-gray-50 transition disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={uploading || !proofImage}
              className="flex-1 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {uploading ? '⏳ Uploading...' : '✅ Confirm Payment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
