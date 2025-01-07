import { TestConnection } from './components/TestConnection';
import { TestButton } from './components/TestButton';

function App() {
  return (
    <div style={{ 
      padding: '50px', 
      backgroundColor: 'red', 
      color: 'white',
      fontSize: '24px'
    }}>
      <h1>!!!VERY OBVIOUS TEST!!!</h1>
      <button 
        onClick={() => alert('Button clicked!')}
        style={{ padding: '20px', fontSize: '20px' }}
      >
        Click This Big Button
      </button>
    </div>
  );
}

export default App;