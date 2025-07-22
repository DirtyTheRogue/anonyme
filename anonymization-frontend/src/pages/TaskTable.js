import React, { useState } from "react";

function TaskTable() {
  const [tasks, setTasks] = useState([
    { id: 1, name: "Extraction", status: "En attente" },
    { id: 2, name: "Anonymisation", status: "En attente" },
    { id: 3, name: "Évaluation", status: "En attente" },
  ]);

  const updateTaskStatus = (id, status) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === id ? { ...task, status: status } : task
      )
    );
  };

  return (
    <div>
      <h2>Liste des Tâches</h2>
      <table>
        <thead>
          <tr>
            <th>Tâche</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td>{task.name}</td>
              <td>{task.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TaskTable;
