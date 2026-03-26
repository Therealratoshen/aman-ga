import { useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ReceiptValidation() {
  const router = useRouter();
  const [token, setToken] = useState(typeof window !== 'undefined' ? localStorage.getItem('token') : null);
  const [formData, setFormData] = useState({
    bank_name: 'BCA',
    transaction_id: '',
    transaction_date: new Date().toISOString().slice(0, 16),
    amount: ''
  });
  const [proofImage, setProofImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    if (!proofImage) {
      setError('Please upload a receipt image');
      setLoading(false);
      return;
    }

    const form = new FormData();
    form.append('bank_name', formData.bank_name);
    form.append('transaction_id', formData.transaction_id);
    form.append('transaction_date', formData.transaction_date);
    form.append('amount', parseInt(formData.amount));
    form.append('proof_image', proofImage);

    try {
      const res = await axios.post(`${API_URL}/receipt/validate`, form, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Validation failed');
    }

    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  if (!token) {
    router.push('/');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-green-600">aman ga?</h1>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
              Receipt Validator
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
            >
              Back to Dashboard
            </button>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl p-6 shadow-lg mb-8">
          <h2 className="text-2xl font-bold mb-6 text-center">Receipt Validation</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium mb-2">
                📸 Upload Receipt/Screenshot
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-green-500 transition">
                {imagePreview ? (
                  <div>
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="max-h-60 mx-auto rounded-lg mb-4 border"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        setProofImage(null);
                        setImagePreview(null);
                      }}
                      className="text-sm text-red-500 hover:underline"
                    >
                      Remove Image
                    </button>
                  </div>
                ) : (
                  <div>
                    <div className="text-4xl mb-2">📁</div>
                    <p className="text-sm text-gray-600 mb-2">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-400">
                      PNG, JPG up to 10MB
                    </p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="mt-2 w-full text-sm text-gray-500"
                      required
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Receipt Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Bank Name */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  🏦 Bank / E-Wallet
                </label>
                <select
                  value={formData.bank_name}
                  onChange={(e) => setFormData({...formData, bank_name: e.target.value})}
                  className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="BCA">BCA (Bank Central Asia)</option>
                  <option value="BRI">BRI (Bank Rakyat Indonesia)</option>
                  <option value="BNI">BNI (Bank Negara Indonesia)</option>
                  <option value="MANDIRI">Mandiri (Bank Mandiri)</option>
                  <option value="PERMATA">Permata (Bank Permata)</option>
                  <option value="DANAMON">Danamon (Bank Danamon)</option>
                  <option value="CIMB">CIMB (Bank CIMB Niaga)</option>
                  <option value="MAYBANK">Maybank (Bank Maybank)</option>
                  <option value="BTN">BTN (Bank Tabungan Negara)</option>
                  <option value="GOPAY">GoPay</option>
                  <option value="OVO">OVO</option>
                  <option value="DANA">DANA</option>
                  <option value="LINKAJA">LinkAja</option>
                  <option value="ALFAMART">Alfamart</option>
                  <option value="INDOMARET">Indomaret</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>

              {/* Amount */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  💰 Amount (Rp)
                </label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({...formData, amount: e.target.value})}
                  className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., 100000"
                  required
                />
              </div>

              {/* Receipt ID */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  🧾 Receipt ID
                </label>
                <input
                  type="text"
                  value={formData.transaction_id}
                  onChange={(e) => setFormData({...formData, transaction_id: e.target.value})}
                  className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., RCP123456789 or TRX123456789"
                  required
                />
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
            </div>

            {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading || !proofImage}
                className="w-full py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg"
              >
                {loading ? '🔍 Validating Receipt...' : '🔍 Validate Receipt'}
              </button>
            </div>
          </form>
        </div>

        {/* Results Section */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
            <h3 className="text-lg font-bold text-red-700 mb-2">❌ Error</h3>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <h3 className="text-xl font-bold mb-4">📋 Validation Results</h3>
              
              {/* OCR Results */}
              {result.ocr && (
                <div className="mb-6">
                  <h4 className="font-bold text-lg mb-3">📝 OCR Results</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className={`p-4 rounded-lg ${result.ocr.matches_form ? 'bg-green-50' : 'bg-red-50'}`}>
                      <p className="font-semibold">Amount:</p>
                      <p>Rp {result.ocr.extracted_amount?.toLocaleString('id-ID') || 'Not detected'}</p>
                    </div>
                    <div className={`p-4 rounded-lg ${result.ocr.matches_form ? 'bg-green-50' : 'bg-red-50'}`}>
                      <p className="font-semibold">Confidence:</p>
                      <p>{Math.round(result.ocr.confidence)}%</p>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Transaction ID:</p>
                      <p>{result.ocr.extracted_transaction_id || 'Not detected'}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Bank:</p>
                      <p>{result.ocr.extracted_bank || 'Not detected'}</p>
                    </div>
                  </div>
                  
                  {!result.ocr.matches_form && result.ocr.mismatches && (
                    <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                      <p className="font-semibold text-yellow-700">⚠️ Mismatches:</p>
                      <ul className="list-disc pl-5 mt-2">
                        {result.ocr.mismatches.map((mismatch, idx) => (
                          <li key={idx}>{mismatch}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Image Analysis */}
              {result.image_analysis && (
                <div className="mb-6">
                  <h4 className="font-bold text-lg mb-3">🖼️ Image Analysis</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className={`p-4 rounded-lg ${result.image_analysis.manipulation_detected ? 'bg-red-50' : 'bg-green-50'}`}>
                      <p className="font-semibold">Manipulation:</p>
                      <p>{result.image_analysis.manipulation_detected ? 'Detected' : 'None detected'}</p>
                    </div>
                    <div className={`p-4 rounded-lg ${result.image_analysis.risk_level === 'LOW' ? 'bg-green-50' : result.image_analysis.risk_level === 'MEDIUM' ? 'bg-yellow-50' : 'bg-red-50'}`}>
                      <p className="font-semibold">Risk Level:</p>
                      <p>{result.image_analysis.risk_level}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Quality Score:</p>
                      <p>{Math.round(result.image_analysis.quality_score * 100)}%</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Deepfake Analysis */}
              {result.deepfake_analysis && (
                <div className="mb-6">
                  <h4 className="font-bold text-lg mb-3">🎭 Deepfake Analysis</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className={`p-4 rounded-lg ${result.deepfake_analysis.is_likely_deepfake ? 'bg-red-50' : 'bg-green-50'}`}>
                      <p className="font-semibold">Is Likely Deepfake:</p>
                      <p>{result.deepfake_analysis.is_likely_deepfake ? 'Yes' : 'No'}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Confidence Score:</p>
                      <p>{Math.round(result.deepfake_analysis.confidence_score * 100)}%</p>
                    </div>
                  </div>
                  
                  {result.deepfake_analysis.indicators && result.deepfake_analysis.indicators.length > 0 && (
                    <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                      <p className="font-semibold text-yellow-700">🔍 Indicators:</p>
                      <ul className="list-disc pl-5 mt-2">
                        {result.deepfake_analysis.indicators.map((indicator, idx) => (
                          <li key={idx}>{indicator}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className={`mt-4 p-4 rounded-lg ${result.deepfake_analysis.is_likely_deepfake ? 'bg-red-100 border border-red-200' : 'bg-green-100 border border-green-200'}`}>
                    <p className="font-semibold">Recommendation:</p>
                    <p>{result.deepfake_analysis.recommendation}</p>
                  </div>
                </div>
              )}

              {/* Receipt Validation */}
              {result.receipt_validation && (
                <div className="mb-6">
                  <h4 className="font-bold text-lg mb-3">🧾 Receipt Validation</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Format Consistency:</p>
                      <p>{Math.round(result.receipt_validation.format_validation.format_consistency_score)}%</p>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Logical Consistency:</p>
                      <p>{Math.round(result.receipt_validation.logical_consistency_score)}%</p>
                    </div>
                    <div className="p-4 rounded-lg bg-green-50">
                      <p className="font-semibold">Overall Validity:</p>
                      <p>{Math.round(result.receipt_validation.overall_receipt_validity)}%</p>
                    </div>
                    <div className="p-4 rounded-lg bg-purple-50">
                      <p className="font-semibold">Receipt Elements:</p>
                      <p className="text-sm">
                        Header: {result.receipt_validation.format_validation.has_header ? '✅' : '❌'}, 
                        Items: {result.receipt_validation.format_validation.has_items ? '✅' : '❌'}, 
                        Totals: {result.receipt_validation.format_validation.has_totals ? '✅' : '❌'}, 
                        Footer: {result.receipt_validation.format_validation.has_footer ? '✅' : '❌'}
                      </p>
                    </div>
                  </div>
                  
                  {/* Business Information */}
                  {result.receipt_validation.business_info && Object.keys(result.receipt_validation.business_info).length > 0 && (
                    <div className="mb-4">
                      <h5 className="font-semibold mb-2">🏢 Business Information:</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        {result.receipt_validation.business_info.name && (
                          <div className="p-2 bg-gray-50 rounded">Name: {result.receipt_validation.business_info.name}</div>
                        )}
                        {result.receipt_validation.business_info.phone && (
                          <div className="p-2 bg-gray-50 rounded">Phone: {result.receipt_validation.business_info.phone}</div>
                        )}
                        {result.receipt_validation.business_info.address && (
                          <div className="p-2 bg-gray-50 rounded">Address: {result.receipt_validation.business_info.address}</div>
                        )}
                        {result.receipt_validation.business_info.tax_id && (
                          <div className="p-2 bg-gray-50 rounded">Tax ID: {result.receipt_validation.business_info.tax_id}</div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Items and Totals */}
                  {result.receipt_validation.items_and_totals && (
                    <div>
                      <h5 className="font-semibold mb-2">🛒 Items & Totals:</h5>
                      {result.receipt_validation.items_and_totals.items && result.receipt_validation.items_and_totals.items.length > 0 && (
                        <div className="mb-2">
                          <p className="text-sm font-medium">Items:</p>
                          <ul className="text-sm ml-4 list-disc">
                            {result.receipt_validation.items_and_totals.items.map((item, idx) => (
                              <li key={idx}>{item.name} - Qty: {item.quantity} - Price: Rp {item.price_per_unit.toLocaleString('id-ID')}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {result.receipt_validation.items_and_totals.totals && Object.keys(result.receipt_validation.items_and_totals.totals).length > 0 && (
                        <div className="text-sm">
                          <p>Totals: {Object.entries(result.receipt_validation.items_and_totals.totals).map(([key, value]) => 
                            `${key}: Rp ${value.toLocaleString('id-ID')}`
                          ).join(', ')}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Authenticity Assessment */}
              {result.authenticity_assessment && (
                <div>
                  <h4 className="font-bold text-lg mb-3">✅ Authenticity Assessment</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Authenticity Score:</p>
                      <p>{Math.round(result.authenticity_assessment.authenticity_score)}%</p>
                    </div>
                    <div className={`p-4 rounded-lg ${result.authenticity_assessment.is_likely_authentic ? 'bg-green-50' : 'bg-red-50'}`}>
                      <p className="font-semibold">Is Likely Authentic:</p>
                      <p>{result.authenticity_assessment.is_likely_authentic ? 'Yes' : 'No'}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-blue-50">
                      <p className="font-semibold">Confidence Level:</p>
                      <p>{result.authenticity_assessment.confidence_level}</p>
                    </div>
                  </div>
                  
                  <div className={`mt-4 p-4 rounded-lg ${result.authenticity_assessment.is_likely_authentic ? 'bg-green-100 border border-green-200' : 'bg-red-100 border border-red-200'}`}>
                    <p className="font-semibold">Recommendation:</p>
                    <p>{result.authenticity_assessment.recommendation}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}