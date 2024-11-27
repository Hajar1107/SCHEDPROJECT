import matplotlib.pyplot as plt
from io import BytesIO
from django.core.files.base import ContentFile
from typing import List, Union
from pathlib import Path
import numpy as np

class GanttChartGenerator:
    def __init__(self, save_dir: str = "static/images"):
        """Initialize the Gantt chart generator with a save directory."""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.colors = [
            "#FF4B4B", "#FF9933", "#FFD700", "#4169E1", "#32CD32", 
            "#8A2BE2", "#FF69B4", "#808080", "#00FFFF", "#8B4513"
        ]
    
    def generate_chart(
        self,
        sequence: List[int],
        machines: List[str],
        start_times: List[List[int]],
        completion_times: List[List[int]],
        filename: str = "gantt_chart.png"
    ) -> str:
        """
        Generate a Gantt chart for the job scheduling problem.
        
        Args:
            sequence: List of job IDs in scheduled order
            machines: List of machine names
            start_times: 2D matrix [machine_idx][job_idx] of start times
            completion_times: 2D matrix [machine_idx][job_idx] of completion times
            filename: Name of the output file
            
        Returns:
            str: Path to the saved Gantt chart
        """
        # Create figure with appropriate size
        n_machines = len(machines)
        fig_width = max(12, max(np.array(completion_times).flat) / 5)
        fig, ax = plt.subplots(figsize=(fig_width, n_machines * 1.5))
        
        # Plot jobs for each machine
        for machine_idx, machine in enumerate(machines):
            y_position = machine_idx * 4
            
            for job_idx, job_id in enumerate(sequence):
                start = start_times[machine_idx][job_idx]
                end = completion_times[machine_idx][job_idx]
                duration = end - start
                
                if duration > 0:  # Only plot if there's actual processing time
                    # Plot job block
                    ax.broken_barh(
                        [(start, duration)],
                        (y_position, 3),
                        facecolors=self.colors[job_idx % len(self.colors)],
                        edgecolor='black',
                        alpha=0.9
                    )
                    
                    # Add job label
                    ax.text(
                        start + duration/2,
                        y_position + 1.5,
                        f'J{job_id}',
                        ha='center',
                        va='center',
                        color='white',
                        fontweight='bold',
                        fontsize=10
                    )
        
        # Customize chart appearance
        self._customize_chart(ax, machines, completion_times)
        
        # Save and return path
        save_path = self.save_dir / filename
        return self._save_chart(fig, save_path)
    
    def _customize_chart(self, ax, machines: List[str], completion_times: List[List[int]]):
        """Customize the chart appearance with proper styling."""
        # Set axes labels and title
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Machines', fontsize=12, fontweight='bold')
        ax.set_title('Production Schedule Gantt Chart', fontsize=14, fontweight='bold', pad=20)
        
        # Set y-axis labels for machines
        ax.set_yticks([i * 4 + 1.5 for i in range(len(machines))])
        ax.set_yticklabels([f'{m}' for m in machines], fontsize=10)
        
        # Set x-axis limits and grid
        makespan = max(max(row) for row in completion_times)
        ax.set_xlim(-1, makespan + 1)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Add timeline markers
        ax.set_xticks(range(0, makespan + 1, 2))
        
        # Grid and styling
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Style improvements
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def _save_chart(self, fig, save_path: Path) -> str:
        """Save the chart to file and return the path."""
        try:
            # Save to buffer first
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
            buffer.seek(0)
            
            # Save to file
            with open(save_path, 'wb') as f:
                f.write(buffer.read())
            
            plt.close(fig)
            buffer.close()
            
            return str(save_path)
            
        except Exception as e:
            plt.close(fig)
            raise RuntimeError(f"Failed to save Gantt chart: {str(e)}")