import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import './App.css';
import { spec } from './spec';

function App() {
  return (
    <div className="App">
      <SwaggerUI spec={spec} />
    </div>
  );
}

export default App;
