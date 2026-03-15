export default function ServiceCard({ service, onPurchase }) {
  const colorClasses = {
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-600',
      button: 'bg-green-500 hover:bg-green-600'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-600',
      button: 'bg-blue-500 hover:bg-blue-600'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-600',
      button: 'bg-purple-500 hover:bg-purple-600'
    }
  };

  const colors = colorClasses[service.color] || colorClasses.green;

  return (
    <div className={`border-2 ${colors.border} rounded-xl p-6 hover:shadow-xl transition-all duration-300 ${colors.bg}`}>
      {/* Header */}
      <div className="mb-4">
        <h4 className="font-bold text-xl mb-2">{service.name}</h4>
        <p className="text-gray-600 text-sm">{service.desc}</p>
      </div>

      {/* Price */}
      <div className="mb-4">
        <p className="text-3xl font-bold text-gray-800">
          Rp {service.price.toLocaleString('id-ID')}
        </p>
        <p className="text-xs text-gray-500">per use</p>
      </div>

      {/* Features */}
      <ul className="space-y-2 mb-6">
        {service.auto ? (
          <li className="flex items-center text-sm">
            <span className="text-green-500 mr-2">✓</span>
            <span className="text-green-700">⚡ Instant activation</span>
          </li>
        ) : (
          <li className="flex items-center text-sm">
            <span className="text-yellow-500 mr-2">⏳</span>
            <span className="text-yellow-700">5-30 min verification</span>
          </li>
        )}
        <li className="flex items-center text-sm">
          <span className="text-green-500 mr-2">✓</span>
          <span>Valid for 90 days</span>
        </li>
        <li className="flex items-center text-sm">
          <span className="text-green-500 mr-2">✓</span>
          <span>Secure payment</span>
        </li>
      </ul>

      {/* Purchase Button */}
      <button
        onClick={onPurchase}
        className={`w-full py-3 rounded-xl text-white font-medium transition-all duration-300 ${colors.button} transform hover:scale-105`}
      >
        Purchase Now
      </button>
    </div>
  );
}
