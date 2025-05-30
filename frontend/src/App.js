import React, { useState, useRef, useEffect } from 'react';
import { Container, Box, Typography, TextField, Button, Paper, List, ListItem, ListItemText, Drawer, Chip, IconButton, CircularProgress } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import SendIcon from '@mui/icons-material/Send';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PendingIcon from '@mui/icons-material/Pending';
import './App.css';

const getTaskSummary = (tasks) => {
  if (!tasks || tasks.length === 0) return '';
  const lastTask = tasks[tasks.length - 1];
  const agent = lastTask.agent.replace('Agent', '').replace(/([A-Z])/g, ' $1').trim();
  const action = lastTask.function.split('_').join(' ');
  return `${agent}: ${action}`;
};

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [planTasks, setPlanTasks] = useState([]);
  const [sessionId, setSessionId] = useState(Date.now().toString());
  const [sessionData, setSessionData] = useState({});
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]); // Store completed conversations
  const [expandedHistory, setExpandedHistory] = useState(null);
  const messagesEndRef = useRef(null);

  const startNewChat = () => {
    // Save current conversation to history if there are messages and tasks
    if (messages.length > 0 && planTasks.length > 0) {
      setHistory(prev => [
        {
          id: sessionId,
          timestamp: new Date().toLocaleString(),
          messages: messages,
          tasks: planTasks,
          summary: getTaskSummary(planTasks)
        },
        ...prev
      ].slice(0, 5)); // Keep only last 5 conversations
    }
    setMessages([]);
    setPlanTasks([]);
    setInput('');
    setSessionId(Date.now().toString());
    setExpandedHistory(null);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          session_data: sessionData,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Always update session data if it exists
      if (data.session_data) {
        setSessionData(data.session_data);
        // Update plan tasks if present in response
        if (data.session_data && data.session_data.plan) {
          // Keep existing task statuses when updating plan
          const existingTaskStatuses = planTasks.reduce((acc, task) => {
            acc[`${task.agent}.${task.function}`] = task.status;
            return acc;
          }, {});

          setPlanTasks(data.session_data.plan.map(task => {
            const taskId = `${task[0]}.${task[1]}`;
            return {
              name: `${taskId}()`,
              agent: task[0],
              function: task[1],
              status: data.status === 'complete' ? 'complete' : existingTaskStatuses[taskId] || 'pending'
            };
          }));
        }
      }

      const formatResponseField = (key, value, prefix = '') => {
        if (typeof value === 'object' && value !== null) {
          if (Array.isArray(value)) {
            return `${prefix}${key}: ${value.join(', ')}`;
          }
          const nestedEntries = Object.entries(value)
            .map(([k, v]) => formatResponseField(k, v, `${prefix}  `))
            .join('\n');
          return `${prefix}${key}:\n${nestedEntries}`;
        }
        return `${prefix}${key}: ${value}`;
      };

      const formatResponse = (data) => {
        if (!data) return 'No response data';

        // Handle response with data field (like insurance verification)
        if (data.data && typeof data.data === 'object') {
          const { provider, service_covered, coverage_details } = data.data;
          return [
            'Insurance Verification Results:',
            `Provider: ${provider}`,
            `Service Coverage: ${service_covered ? 'Covered' : 'Not Covered'}`,
            `Copay: $${coverage_details?.copay || 'N/A'}`,
            `Authorization Required: ${coverage_details?.requires_authorization ? 'Yes' : 'No'}`
          ].join('\n');
        }

        // String response
        if (typeof data.response === 'string') {
          return data.response;
        }

        // Array response
        if (Array.isArray(data.response)) {
          return data.response.join('\n');
        }

        // Object response
        if (typeof data.response === 'object' && data.response !== null) {
          if (data.response.message) {
            return data.response.message;
          }
          const entries = Object.entries(data.response)
            .filter(([key]) => !['session_data', 'status'].includes(key))
            .map(([key, value]) => formatResponseField(key, value));
          return entries.length > 0 ? entries.join('\n') : 'Operation completed successfully';
        }

        return 'Operation completed successfully';
      };

      if (data.status === 'need_input') {
        setMessages(prev => [...prev, { text: data.prompt.replace(/^response:\s*/i, ''), sender: 'bot' }]);
      } else {
        const responseText = formatResponse(data);
        setMessages(prev => [...prev, { text: responseText.replace(/^response:\s*/i, ''), sender: 'bot' }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: `Sorry, there was an error processing your request. ${error.message}`, 
        sender: 'bot' 
      }]);
    }
    setIsLoading(false);
  };

  const drawerWidth = 240;

  return (
    <div className="App">
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: 'background.default',
            borderRight: 1,
            borderColor: 'divider'
          },
        }}
        anchor="left"
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
            <Button
              variant="contained"
              fullWidth
              onClick={startNewChat}
              sx={{ mb: 2 }}
              startIcon={<RefreshIcon />}
            >
              New Chat
            </Button>
          </Box>

          {/* Current Plan Section */}
          <Box sx={{ p: 2, flex: '0 0 auto', borderBottom: '1px solid #e0e0e0' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Current Plan
            </Typography>
            {planTasks.length > 0 && (
              <List sx={{ p: 0 }}>
                {planTasks.map((task, index) => (
                  <ListItem key={index} sx={{ p: 2, bgcolor: 'background.paper' }}>
                    <ListItemText 
                      primary={task.name}
                      secondary={`Step ${index + 1} of ${planTasks.length}`}
                    />
                    <Chip
                      label={task.status || 'pending'}
                      color={task.status === 'complete' ? 'success' : 'warning'}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            )}
            {planTasks.length === 0 && (
              <Typography color="textSecondary" sx={{ textAlign: 'center' }}>
                No active plan
              </Typography>
            )}
          </Box>

          {/* History Section */}
          <Box sx={{ p: 2, flex: 1, overflow: 'auto' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              History
            </Typography>
            {history.map((conv) => (
              <Paper key={conv.id} sx={{ mb: 1, overflow: 'hidden' }}>
                <Button
                  fullWidth
                  onClick={() => setExpandedHistory(expandedHistory === conv.id ? null : conv.id)}
                  sx={{
                    p: 2,
                    justifyContent: 'space-between',
                    textAlign: 'left',
                    textTransform: 'none'
                  }}
                >
                  <Box>
                    <Typography variant="subtitle2" color="primary">
                      {getTaskSummary(conv.tasks)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {conv.timestamp}
                    </Typography>
                  </Box>
                  {expandedHistory === conv.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </Button>
                {expandedHistory === conv.id && (
                  <List sx={{ p: 0, bgcolor: 'background.paper' }}>
                    {conv.tasks.map((task, index) => (
                      <ListItem key={index} sx={{ pl: 3, pr: 2 }}>
                        <ListItemText
                          primary={task.name}
                          secondary={`Step ${index + 1} of ${conv.tasks.length}`}
                        />
                        <Chip
                          label="complete"
                          color="success"
                          size="small"
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </Paper>
            ))}
            {history.length === 0 && (
              <Typography color="textSecondary" sx={{ textAlign: 'center' }}>
                No conversation history
              </Typography>
            )}
          </Box>
        </Box>
      </Drawer>
      
      <Container maxWidth="lg" sx={{ 
        height: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        ml: '340px' // Adjust main content to account for drawer width
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', p: 2, borderBottom: '1px solid #e0e0e0' }}>
          <img src="/OZ-logo.png" alt="OZ" style={{ height: 40, marginRight: 16 }} />
          <Typography variant="h5">Healthcare Assistant</Typography>
        </Box>

        <Box sx={{ 
          flex: 1, 
          overflowY: 'auto', 
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}>
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: message.sender === 'user' ? '#0066cc' : '#f5f5f5',
                  color: message.sender === 'user' ? 'white' : 'inherit',
                  borderRadius: 2
                }}
              >
                <Typography>{message.text}</Typography>
              </Paper>
            </Box>
          ))}
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
              <CircularProgress size={20} />
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        <Paper 
          elevation={3} 
          sx={{ 
            p: 2, 
            borderTop: '1px solid #e0e0e0',
            borderRadius: '0',
            bgcolor: '#f5f5f5'
          }}
        >
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              variant="outlined"
              sx={{
                bgcolor: 'white',
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2
                }
              }}
            />
            <IconButton onClick={sendMessage} disabled={isLoading} color="primary">
              {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
            </IconButton>
          </Box>
        </Paper>
      </Container>
    </div>
  );
}

export default App;
