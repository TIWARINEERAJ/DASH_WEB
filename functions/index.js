const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

// Process new sensor data
exports.processSensorData = functions.firestore
  .document('sensor_data/{docId}')
  .onCreate((snap, context) => {
    const data = snap.data();
    
    // Example: Calculate average if temperature exists
    if (data.temperature) {
      // Get the last 10 temperature readings
      return admin.firestore().collection('sensor_data')
        .orderBy('timestamp', 'desc')
        .limit(10)
        .get()
        .then(snapshot => {
          let sum = 0;
          let count = 0;
          
          snapshot.forEach(doc => {
            const docData = doc.data();
            if (docData.temperature) {
              sum += docData.temperature;
              count++;
            }
          });
          
          const average = count > 0 ? sum / count : 0;
          
          // Store the result in a stats collection
          return admin.firestore().collection('stats').add({
            type: 'temperature_average',
            value: average,
            samples: count,
            timestamp: admin.firestore.FieldValue.serverTimestamp()
          });
        });
    }
    
    return null;
  });

// Process new predictions
exports.processPredictions = functions.firestore
  .document('predictions/{docId}')
  .onCreate((snap, context) => {
    const data = snap.data();
    
    // Example: Calculate average prediction error (if we have actual data)
    if (data.temperature) {
      const predictionDate = data.date;
      
      // Format the date to match our timestamp format
      const dateStr = predictionDate.toDate().toISOString().split('T')[0];
      
      // Check if we have actual data for this prediction
      return admin.firestore().collection('sensor_data')
        .where('date', '>=', dateStr)
        .where('date', '<', dateStr + '\uf8ff') // End of the day
        .limit(1)
        .get()
        .then(snapshot => {
          if (snapshot.empty) {
            console.log('No actual data found for the prediction date');
            return null;
          }
          
          // Calculate prediction error
          const actualData = snapshot.docs[0].data();
          const error = data.temperature - actualData.temperature;
          
          // Store prediction error stats
          return admin.firestore().collection('stats').add({
            type: 'prediction_error',
            value: error,
            prediction: data.temperature,
            actual: actualData.temperature,
            date: predictionDate,
            timestamp: admin.firestore.FieldValue.serverTimestamp()
          });
        });
    }
    
    return null;
  });

// HTTP endpoint to get latest statistics
exports.getStats = functions.https.onRequest((req, res) => {
  // Set CORS headers
  res.set('Access-Control-Allow-Origin', '*');
  
  if (req.method === 'OPTIONS') {
    // Send response to OPTIONS requests
    res.set('Access-Control-Allow-Methods', 'GET');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.status(204).send('');
    return;
  }
  
  return admin.firestore().collection('stats')
    .orderBy('timestamp', 'desc')
    .limit(5)
    .get()
    .then(snapshot => {
      const stats = [];
      snapshot.forEach(doc => {
        stats.push(doc.data());
      });
      
      res.json({ stats });
    })
    .catch(error => {
      console.error('Error getting stats:', error);
      res.status(500).json({ error: error.message });
    });
}); 