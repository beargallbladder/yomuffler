# 🚀 Global Cursor Workflow Directive

## Core Principle: Swarm vs. Hive-Mind

This project uses a **swarm-based approach** for all tasks. Each agent operates independently while contributing to collective goals.

### 🎯 Key Directives

1. **Always Use Swarm Mode** for:
   - Feature implementation
   - Bug fixes
   - Code refactoring
   - Documentation updates
   - Testing and validation

2. **Required Agent Outputs**:
   - ✅ Working code implementations
   - ✅ Execution traces and logs
   - ✅ Memory persistence tags
   - ✅ Session continuity markers

3. **Workflow Standards**:
   - Each task must be atomic and self-contained
   - Agents must persist their state for session continuity
   - All code changes must include validation steps
   - Documentation must be updated in parallel with code

### 🧩 Implementation Guidelines

#### For Cursor Agents:
```bash
# Start every session with:
./claude-flow swarm "<task_description>" --persist --trace --validate

# For complex features:
./claude-flow swarm "<feature>" --strategy development --mode distributed --parallel
```

#### For Manual Development:
1. Break tasks into atomic units
2. Document decision rationale
3. Include test validation
4. Update relevant documentation

### 📊 Success Metrics

- **Code Coverage**: Maintain >80% test coverage
- **Documentation**: Every feature must have docs
- **Performance**: All changes must pass performance benchmarks
- **Integration**: Changes must not break existing integrations

### 🔄 Session Continuity

When resuming work:
1. Check previous session state in `.cursor/sessions/`
2. Review memory tags in `./claude-flow memory list`
3. Continue from last checkpoint

### 🚨 Important Notes

- **NO HIVE-MIND MODE**: Individual agent autonomy is paramount
- **PERSIST EVERYTHING**: Use memory tags for cross-session continuity
- **VALIDATE ALWAYS**: Every change must be tested before commit

---

*This directive ensures consistent, high-quality development across all Cursor and Claude Flow sessions.*