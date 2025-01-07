import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ 
      padding: '50px', 
      backgroundColor: 'red', 
      color: 'white',
      fontSize: '24px',
      textAlign: 'center'
    }}>
      <h1>!!!VERY OBVIOUS TEST i am testing 123 !!!</h1>
      <div>Count: {count}</div>
      <button 
        onClick={() => setCount(c => c + 1)}
        style={{ 
          padding: '20px', 
          fontSize: '20px', 
          margin: '20px',
          cursor: 'pointer'
        }}
      >
        Click to Count Up
      </button>
    </div>
  );
}

export default App;
